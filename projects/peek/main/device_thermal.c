/* SPDX-License-Identifier: Apache-2.0 */
#include "device_thermal.h"
#include "peek_ui.h"
#include "mosaico_module_thermal.h"
#include "mosaico_module_mgr.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include <stdlib.h>
#include <inttypes.h>
#ifdef ESP_PLATFORM
#include "sdkconfig.h"
#endif
/* Sensor task owns the driver. Render-task timer, event and canvas callbacks
 * exclusively own view/detector. Queue copies immutable complete frames.
 * Latest-only mailbox may drop frames; it never duplicates them. */
static struct {
    QueueHandle_t queue;peek_ui_t view;void *timer;
    peek_frame_t incoming;
} *app;
typedef struct {bool ok;uint64_t sequence,ms;mosaico_thermal_frame_t raw;} capture_t;
static const char *TAG="peek_thermal";
static uint64_t now_ms(void){return (uint64_t)esp_timer_get_time()/1000;}
static void sensor_task(void *ctx)
{
    capture_t *message=ctx;uint64_t sequence=0;
    mosaico_module_lease_t lease={0};mosaico_thermal_handle_t sensor=NULL;
    for(;;){
        if(!sensor){
            mosaico_module_mgr_claim_config_t claim={.expected_type=MOSAICO_BOARD_TYPE_THERMAL,.slot=MOSAICO_MODULE_MGR_SLOT_AUTO,.timeout_ms=500};
            esp_err_t error=mosaico_module_mgr_claim(&claim,&lease);
            if(error==ESP_OK){
                mosaico_thermal_config_t config=MOSAICO_THERMAL_DEFAULT_CONFIG();
                error=mosaico_thermal_new((bsp_subboard_slot_t)lease.slot,&config,&sensor);
            }
            if(error!=ESP_OK){
                /* Failed creation can retain a handle if device removal failed. */
                while(sensor){
                    esp_err_t cleanup=mosaico_thermal_del(sensor);
                    if(cleanup==ESP_OK)sensor=NULL;
                    else {ESP_LOGE(TAG,"cleanup: %s",esp_err_to_name(cleanup));vTaskDelay(pdMS_TO_TICKS(500));}
                }
                if(lease.id){
                    esp_err_t release=mosaico_module_mgr_release(&lease);
                    if(release!=ESP_OK){ESP_LOGE(TAG,"slot release: %s",esp_err_to_name(release));vTaskDelete(NULL);return;}
                }
                message->ok=false;message->ms=now_ms();xQueueOverwrite(app->queue,message);
                vTaskDelay(pdMS_TO_TICKS(500));continue;
            }
            ESP_LOGI(TAG,"MLX90640 slot=%u I2C=0x33/400000Hz subpage=16Hz full-frame~=8Hz",lease.slot);
        }
        esp_err_t error=mosaico_thermal_read(sensor,&message->raw,1000);
        message->ok=error==ESP_OK;message->ms=now_ms();
        if(message->ok)message->sequence=++sequence;
        else ESP_LOGW(TAG,"complete-frame read failed: %s; previous pixels not resubmitted",esp_err_to_name(error));
        xQueueOverwrite(app->queue,message);
        if(error!=ESP_OK)vTaskDelay(pdMS_TO_TICKS(20));
    }
}
static void refresh(esp_gsp_handle_t ui,void *ctx)
{
    (void)ui;capture_t *message=ctx;
    bool received=xQueueReceive(app->queue,message,0)==pdTRUE;
    /* Read processing time after dequeue: another core can publish a frame
     * between a pre-dequeue clock read and the queue operation. */
    uint64_t now=now_ms();
    if(received){
        if(message->ok){
            peek_frame_t *f=&app->incoming;
            f->sequence=message->sequence;f->captured_ms=message->ms;f->complete=true;
            for(unsigned i=0;i<768;i++){f->c[i]=message->raw.pixels[i];f->valid[i]=1;}
            (void)peek_ui_submit(&app->view,f,now);
        }else (void)peek_fault(&app->view.detector,now);
    }
    peek_ui_refresh(&app->view,now);
}
esp_err_t device_thermal_start(esp_gsp_handle_t ui)
{
    if(!ui)return ESP_ERR_INVALID_ARG;
    if(app)return ESP_ERR_INVALID_STATE;
    app=calloc(1,sizeof(*app));capture_t *producer=calloc(1,sizeof(*producer)),*consumer=calloc(1,sizeof(*consumer));
    if(!app||!producer||!consumer){free(app);app=NULL;free(producer);free(consumer);return ESP_ERR_NO_MEM;}
    app->queue=xQueueCreate(1,sizeof(capture_t));
    if(!app->queue){free(producer);free(consumer);free(app);app=NULL;return ESP_ERR_NO_MEM;}
    esp_err_t rc=mosaico_module_mgr_init(NULL);
    if(rc!=ESP_OK)goto fail;
    rc=peek_ui_init(&app->view,ui,NULL,NULL);if(rc!=ESP_GSP_OK)goto fail_ui;
#ifdef CONFIG_PEEK_DIAGNOSTIC_VIEW
    rc=peek_ui_set_view(&app->view,false);
#else
    rc=peek_ui_set_view(&app->view,true);
#endif
    if(rc!=ESP_GSP_OK)goto fail_ui;
    app->view.live=true;app->view.source="LIVE / MLX90640 (native orientation)";
    app->timer=esp_gsp_timer_create(ui,33,refresh,consumer);
    if(!app->timer){rc=ESP_ERR_NO_MEM;goto fail_ui;}
    if(xTaskCreate(sensor_task,"peek_capture",8192,producer,5,NULL)!=pdPASS){rc=ESP_ERR_NO_MEM;goto fail_ui;}
    return ESP_OK;
fail_ui:
    {
        esp_gsp_err_t timer_error=ESP_GSP_OK;
        if(app->timer)timer_error=esp_gsp_timer_delete(ui,app->timer);
        esp_gsp_err_t detach_error=peek_ui_deinit(&app->view);
        /* Both cancellation and the render-task barrier must succeed. On
         * failure keep every possibly referenced context alive for app life. */
        if(timer_error!=ESP_GSP_OK || detach_error!=ESP_GSP_OK || esp_gsp_flush(ui,1000)!=ESP_GSP_OK){
            ESP_LOGE(TAG,"GSP cleanup incomplete; retaining callback contexts until reboot");
            free(producer);return rc;
        }
    }
fail:
    peek_ui_release(&app->view);
    vQueueDelete(app->queue);free(producer);free(consumer);free(app);app=NULL;return rc;
}

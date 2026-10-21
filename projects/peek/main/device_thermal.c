/* SPDX-License-Identifier: Apache-2.0 */
#include "device_thermal.h"
#include "peek_ui.h"
#include "peek_live.h"
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
#include "device_status.h"
#endif
/* Sensor task owns driver, detector and role observation history. Render task
 * owns its independent view/canvas state. Latest-only mailbox drops display
 * snapshots, never complete samples before detection. */
static struct {
    QueueHandle_t queue;peek_ui_t view;void *timer;
} *app;
typedef struct {peek_live_t live;peek_frame_t incoming;mosaico_thermal_frame_t raw;} producer_t;
static void publish_input(producer_t *p,bool ok,uint64_t sequence,uint64_t now){
    peek_frame_t *f=&p->incoming;
    if(ok){
        f->sequence=sequence;f->captured_ms=now;f->complete=true;
        for(unsigned i=0;i<768;i++){f->c[i]=p->raw.pixels[i];f->valid[i]=1;}
    }
    if(!peek_live_event(&p->live,ok?f:NULL,!ok,now)){
        ESP_LOGE("peek_thermal","live state clock failure");return;
    }
#ifdef ESP_PLATFORM
    device_status_capture(ok);
#endif
    xQueueOverwrite(app->queue,&p->live);
}
static const char *TAG="peek_thermal";
static uint64_t now_ms(void){return (uint64_t)esp_timer_get_time()/1000;}
static void sensor_task(void *ctx)
{
    producer_t *producer=ctx;uint64_t sequence=0;
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
                publish_input(producer,false,sequence,now_ms());
                vTaskDelay(pdMS_TO_TICKS(500));continue;
            }
            ESP_LOGI(TAG,"MLX90640 slot=%u I2C=0x33/400000Hz subpage=16Hz full-frame~=8Hz",lease.slot);
        }
        esp_err_t error=mosaico_thermal_read(sensor,&producer->raw,1000);
        uint64_t captured=now_ms();
        if(error==ESP_OK)sequence++;
        else ESP_LOGW(TAG,"complete-frame read failed: %s; previous pixels not resubmitted",esp_err_to_name(error));
        publish_input(producer,error==ESP_OK,sequence,captured);
        if(error!=ESP_OK)vTaskDelay(pdMS_TO_TICKS(20));
    }
}
static void refresh(esp_gsp_handle_t ui,void *ctx)
{
    (void)ui;peek_live_t *snapshot=ctx;
    bool received=xQueueReceive(app->queue,snapshot,0)==pdTRUE;
    uint64_t now=now_ms();
    if(received){
        /* Detection and role evidence already consumed every complete frame
         * on the acquisition task. Render owns this independent copy. */
        app->view.detector=snapshot->detector;app->view.dragon=snapshot->dragon;
        app->view.displayed=snapshot->displayed;app->view.has_frame=snapshot->has_frame;
    }
    peek_ui_refresh(&app->view,now);
#ifdef ESP_PLATFORM
    device_status_publish(&app->view,now);
#endif
}
esp_err_t device_thermal_start(esp_gsp_handle_t ui)
{
    if(!ui)return ESP_ERR_INVALID_ARG;
    if(app)return ESP_ERR_INVALID_STATE;
    app=calloc(1,sizeof(*app));producer_t *producer=calloc(1,sizeof(*producer));peek_live_t *consumer=calloc(1,sizeof(*consumer));
    if(!app||!producer||!consumer){free(app);app=NULL;free(producer);free(consumer);return ESP_ERR_NO_MEM;}
    app->queue=xQueueCreate(1,sizeof(peek_live_t));
    if(!app->queue){free(producer);free(consumer);free(app);app=NULL;return ESP_ERR_NO_MEM;}
    if(!peek_live_init(&producer->live)){vQueueDelete(app->queue);free(producer);free(consumer);free(app);app=NULL;return ESP_ERR_INVALID_STATE;}
    esp_err_t rc=mosaico_module_mgr_init(NULL);
    if(rc!=ESP_OK)goto fail;
    rc=peek_ui_init(&app->view,ui,NULL,NULL);if(rc!=ESP_GSP_OK)goto fail_ui;
#ifdef ESP_PLATFORM
    app->view.sample_step=CONFIG_PEEK_EYE_SAMPLE_STEP;
#endif
#ifdef CONFIG_PEEK_DIAGNOSTIC_VIEW
    rc=peek_ui_set_view(&app->view,false);
#else
    rc=peek_ui_set_view(&app->view,true);
#endif
    if(rc!=ESP_GSP_OK)goto fail_ui;
    app->view.live=true;app->view.source="LIVE / MLX90640 (native orientation)";
    app->timer=esp_gsp_timer_create(ui,33,refresh,consumer);
    if(!app->timer){rc=ESP_ERR_NO_MEM;goto fail_ui;}
#if defined(ESP_PLATFORM) && CONFIG_FREERTOS_NUMBER_OF_CORES > 1
    /* A task doing floating-point work may become core-affine in this SDK.
     * Observe the initialized GSP owner after its first callback, then create
     * the sensor owner on the other core. No driver/GSP implementation edit. */
    int render_core=-1;
    for(unsigned waited=0;waited<1000 && render_core<0;waited+=10){
        render_core=device_status_render_core();
        if(render_core<0)vTaskDelay(pdMS_TO_TICKS(10));
    }
    if(render_core<0 || render_core>1){rc=ESP_ERR_TIMEOUT;goto fail_ui;}
    int capture_core=1-render_core;
    if(xTaskCreatePinnedToCore(sensor_task,"peek_capture",8192,producer,5,NULL,capture_core)!=pdPASS){rc=ESP_ERR_NO_MEM;goto fail_ui;}
    ESP_LOGI(TAG,"owners: GSP core=%d; MLX90640/detector/role core=%d",render_core,capture_core);
#else
    if(xTaskCreate(sensor_task,"peek_capture",8192,producer,5,NULL)!=pdPASS){rc=ESP_ERR_NO_MEM;goto fail_ui;}
#endif
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

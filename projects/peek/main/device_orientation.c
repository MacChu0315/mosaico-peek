/* SPDX-License-Identifier: Apache-2.0 */
#include "device_orientation.h"
#include "peek_orientation.h"
#include "bsp/imu.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"
#include <math.h>
static portMUX_TYPE orientation_lock=portMUX_INITIALIZER_UNLOCKED;
static device_orientation_status_t status;
static bool running;
void device_orientation_read(device_orientation_status_t *out){
    portENTER_CRITICAL(&orientation_lock);*out=status;portEXIT_CRITICAL(&orientation_lock);
}
static void publish(const device_orientation_status_t *s){
    portENTER_CRITICAL(&orientation_lock);status=*s;portEXIT_CRITICAL(&orientation_lock);
}
#ifdef CONFIG_PEEK_AUTO_ORIENTATION
static void sample_once(peek_orientation_t *classifier){
    device_orientation_status_t next;device_orientation_read(&next);
    float ax=0,ay=0,az=0,gx=0,gy=0,gz=0;
    next.error=bsp_imu_get_accel(&ax,&ay,&az);
    if(next.error==ESP_OK)next.error=bsp_imu_get_gyro(&gx,&gy,&gz);
    next.sampled_ms=(uint64_t)esp_timer_get_time()/1000;next.samples++;
    /* Board30:ed:a0:f4:52:a0, user-labelled poses: upright accel +Y;
     * clockwise90 accel -X. Screen axes (+right,+down) have opposite XY
     * handedness to the sensor, so a mounting rotation alone is insufficient.
     * Convert to screen gravity-down first, then apply optional mounting. */
    float x=-ax,y=ay;
    switch(CONFIG_PEEK_IMU_MOUNT_QUARTERS){
        case 1:x=-ay;y=-ax;break;
        case 2:x=ax;y=-ay;break;
        case 3:x=ay;y=ax;break;
    }
    peek_orientation_sample(classifier,x,y,-az,sqrtf(gx*gx+gy*gy+gz*gz),next.error==ESP_OK,next.sampled_ms);
    next.rotation=classifier->rotation;
    /* Keep last finite raw reading on failure so JSON diagnostics stay valid. */
    if(next.error==ESP_OK&&isfinite(ax)&&isfinite(ay)&&isfinite(az)){next.ax=ax;next.ay=ay;next.az=az;}
    publish(&next);
}
static void orientation_task(void *context){
    (void)context;peek_orientation_t classifier={.rotation=CONFIG_PEEK_FIXED_ORIENTATION*90};
    for(;;){sample_once(&classifier);vTaskDelay(pdMS_TO_TICKS(20));}
}
#endif
esp_err_t device_orientation_start(void){
    if(running)return ESP_ERR_INVALID_STATE;
    device_orientation_status_t next={.rotation=CONFIG_PEEK_FIXED_ORIENTATION*90};
#ifdef CONFIG_PEEK_AUTO_ORIENTATION
    next.automatic=true;
    next.error=bsp_imu_init();
    /* The0.2 driver can retain a cleanup-only handle after failed init.
     * INVALID_STATE denotes an existing owner; do not tear that owner down. */
    if(next.error!=ESP_OK&&next.error!=ESP_ERR_INVALID_STATE){
        esp_err_t cleanup=bsp_imu_deinit();
        if(cleanup!=ESP_OK)ESP_LOGE("peek_orientation","IMU init cleanup failed: %d",cleanup);
    }
    if(next.error==ESP_OK){
        const bsp_imu_config_t config=BSP_IMU_CONFIG_DEFAULT();
        next.error=bsp_imu_start(&config);
        if(next.error!=ESP_OK){esp_err_t cleanup=bsp_imu_deinit();if(cleanup!=ESP_OK)ESP_LOGE("peek_orientation","IMU cleanup failed: %d",cleanup);}
        else {
            publish(&next);
            if(xTaskCreate(orientation_task,"peek_imu",3072,NULL,4,NULL)==pdPASS){running=true;return ESP_OK;}
            next.error=ESP_ERR_NO_MEM;
            esp_err_t stop=bsp_imu_stop(),cleanup=bsp_imu_deinit();
            if(stop!=ESP_OK||cleanup!=ESP_OK)ESP_LOGE("peek_orientation","IMU cleanup failed: %d/%d",stop,cleanup);
        }
    }
    publish(&next);return next.error;
#else
    publish(&next);running=true;return ESP_OK;
#endif
}

/* SPDX-License-Identifier: Apache-2.0 */
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(p) ((void)(p))
#define portEXIT_CRITICAL(p) ((void)(p))
#include "../projects/peek/main/device_orientation.c"
static int init_error,start_error,read_error,task_error,cleanup_error;
static unsigned stops,deinits;
static float ax=.0529f,ay=.9130f,az=.3854f;
static int64_t clock_us;
esp_err_t bsp_imu_init(void){return init_error;}
esp_err_t bsp_imu_start(const bsp_imu_config_t *c){(void)c;return start_error;}
esp_err_t bsp_imu_stop(void){stops++;return ESP_OK;}
esp_err_t bsp_imu_deinit(void){deinits++;return cleanup_error;}
esp_err_t bsp_imu_get_accel(float *x,float *y,float *z){*x=ax;*y=ay;*z=az;return read_error;}
esp_err_t bsp_imu_get_gyro(float *x,float *y,float *z){*x=*y=*z=0;return read_error;}
int64_t esp_timer_get_time(void){return clock_us;}
int xTaskCreate(void (*fn)(void *),const char *n,unsigned stack,void *ctx,unsigned pri,void *out){(void)fn;(void)n;(void)stack;(void)ctx;(void)pri;(void)out;return task_error?0:pdPASS;}
void vTaskDelay(unsigned ms){(void)ms;}
int main(void){
    init_error=ESP_FAIL;assert(device_orientation_start()==ESP_FAIL);assert(deinits==1);
    cleanup_error=ESP_ERR_NO_MEM;assert(device_orientation_start()==ESP_FAIL&&deinits==2);
    cleanup_error=0;init_error=ESP_ERR_INVALID_STATE;assert(device_orientation_start()==ESP_ERR_INVALID_STATE&&deinits==2);
    init_error=ESP_FAIL;
    device_orientation_status_t out;device_orientation_read(&out);assert(out.error==ESP_ERR_INVALID_STATE&&out.rotation==0);
    init_error=0;start_error=ESP_FAIL;assert(device_orientation_start()==ESP_FAIL);assert(deinits==3);
    start_error=0;task_error=1;assert(device_orientation_start()==ESP_ERR_NO_MEM);assert(stops==1&&deinits==4);
    task_error=0;assert(device_orientation_start()==ESP_OK);
    assert(device_orientation_start()==ESP_ERR_INVALID_STATE);
    peek_orientation_t classifier={0};
    for(int i=0;i<40;i++){clock_us=i*20000;sample_once(&classifier);}
    device_orientation_read(&out);assert(out.rotation==0&&out.samples==40&&out.error==ESP_OK);
    ax=-.4509f;ay=.2338f;az=.8627f;
    for(int i=40;i<80;i++){clock_us=i*20000;sample_once(&classifier);}
    device_orientation_read(&out);assert(out.rotation==270);
    read_error=ESP_FAIL;clock_us=1600000;sample_once(&classifier);
    device_orientation_read(&out);assert(out.rotation==270&&out.error==ESP_FAIL&&out.samples==81);
    read_error=0;ax=0;ay=0;az=1;
    for(int i=81;i<120;i++){clock_us=i*20000;sample_once(&classifier);}
    device_orientation_read(&out);assert(out.rotation==270&&out.error==ESP_OK);
    /* Real board30:ed:a0:f4:52:a0, user-labelled upright. With the old
     * provisional mounting this settles at270 instead of the required0. */
    classifier=(peek_orientation_t){0};ax=.0529f;ay=.9130f;az=.3854f;
    for(int i=120;i<160;i++){clock_us=i*20000;sample_once(&classifier);}
    device_orientation_read(&out);assert(out.rotation==0);
    /* Opposite cardinal vectors extend the two labelled physical axes. */
    ax=0;ay=-1;az=0;
    for(int i=160;i<200;i++){clock_us=i*20000;sample_once(&classifier);}
    device_orientation_read(&out);assert(out.rotation==180);
    ax=1;ay=0;
    for(int i=200;i<240;i++){clock_us=i*20000;sample_once(&classifier);}
    device_orientation_read(&out);assert(out.rotation==90);
    puts("PASS IMU startup cleanup, sampled mounting transform, error/fallback telemetry");
}

/* SPDX-License-Identifier: Apache-2.0 */
/* Read-only acceptance telemetry. The GSP task owns view; RPC copies a small
 * locked snapshot and formats outside the lock. No extra detector observations. */
#include "device_status.h"
#include "esp_iris.h"
#include "esp_gsp_debug.h"
#include "esp_app_desc.h"
#include "peek_build_revision.h"
#include "freertos/FreeRTOS.h"
#include <stdatomic.h>
#include <stdio.h>
#include <inttypes.h>
static atomic_uint_least32_t captures,faults;
static portMUX_TYPE lock=portMUX_INITIALIZER_UNLOCKED;
static struct snapshot {
    uint64_t now,callbacks,draws,draw_us,draw_max,prepares,prepare_us,pixels;
    uint64_t render_busy_us,raster_us,submit_us;
    uint32_t frames;
    peek_result_t result;
    dragon_t role;
    int error;
} snapshot;
void device_status_capture(bool ok){atomic_fetch_add(&captures,1);if(!ok)atomic_fetch_add(&faults,1);}
void device_status_publish(const peek_ui_t *v,uint64_t now){
    struct snapshot s={.now=now,.draws=v->draws,.draw_us=v->render_us_total,.draw_max=v->render_us_max,.prepares=v->prepares,.prepare_us=v->prepare_us_total,.pixels=v->draw_pixels,.result=v->detector.result,.role=v->dragon,.error=v->error};
    esp_gsp_render_stats(v->ui,&s.frames,&s.render_busy_us);
    esp_gsp_render_phases(v->ui,&s.raster_us,&s.submit_us);
    portENTER_CRITICAL(&lock);s.callbacks=snapshot.callbacks+1;snapshot=s;portEXIT_CRITICAL(&lock);
}
static esp_err_t rpc(const esp_iris_rpc_request_t *request,uint8_t *out,size_t capacity,size_t *size,void *ctx){
    (void)ctx;*size=0;if(request->payload_size)return ESP_ERR_INVALID_ARG;
    struct snapshot s;portENTER_CRITICAL(&lock);s=snapshot;portEXIT_CRITICAL(&lock);
    const peek_result_t *r=&s.result;const dragon_t *c=&s.role;
    int n=snprintf((char *)out,capacity,
        "{\"schema\":1,\"source_revision\":\"%s\",\"version\":\"%s\",\"source\":\"LIVE MLX90640\",\"view\":\"dragon\",\"now_ms\":%"PRIu64","
        "\"captures\":%"PRIu32",\"faults\":%"PRIu32",\"callbacks\":%"PRIu64",\"draws\":%"PRIu64",\"draw_us\":%"PRIu64",\"draw_max_us\":%"PRIu64",\"pixels\":%"PRIu64","
        "\"prepares\":%"PRIu64",\"prepare_us\":%"PRIu64",\"render_frames\":%"PRIu32",\"render_busy_us\":%"PRIu64",\"raster_us\":%"PRIu64",\"submit_us\":%"PRIu64",\"error\":%d,"
        "\"sequence\":%"PRIu64",\"samples\":%"PRIu64",\"last_valid_ms\":%"PRIu64",\"data\":\"%s\",\"target\":%s,\"held\":%s,\"x\":%.5f,\"y\":%.5f,"
        "\"role\":\"%s\",\"stationary\":%s,\"observations\":%"PRIu64",\"gaze_x\":%.5f,\"gaze_y\":%.5f,\"blink\":%.5f,\"speed_px_s\":%.5f}",
        PEEK_SOURCE_REVISION,esp_app_get_description()->version,s.now,
        (uint32_t)atomic_load(&captures),(uint32_t)atomic_load(&faults),s.callbacks,s.draws,s.draw_us,s.draw_max,s.pixels,s.prepares,s.prepare_us,s.frames,s.render_busy_us,s.raster_us,s.submit_us,s.error,
        r->sequence,r->accepted_samples,r->last_valid_ms,peek_data_name(r->data),r->has_target?"true":"false",r->held?"true":"false",r->x,r->y,
        dragon_mode_name(c->mode),c->stationary?"true":"false",c->observations,c->pose.gaze_x,c->pose.gaze_y,c->pose.blink,c->speed_px_s);
    if(n<0||(size_t)n>=capacity)return ESP_ERR_INVALID_SIZE;
    *size=(size_t)n;return ESP_OK;
}
esp_err_t device_status_start(void){return esp_iris_rpc_register(0x504c,1,rpc,NULL);}

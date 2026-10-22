/* SPDX-License-Identifier: Apache-2.0 */
/* Exercise actual firmware counters with completed-generation timing stubs. */
#include <assert.h>
#include <string.h>
#include <stdio.h>
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(p) ((void)(p))
#define portEXIT_CRITICAL(p) ((void)(p))
#define ESP_ERR_INVALID_SIZE 0x104
static int xPortGetCoreID(void){return 1;}
#include "../projects/peek/main/device_status.c"
static uint32_t completed;
void esp_gsp_render_stats(esp_gsp_handle_t ui,uint32_t *frames,uint64_t *us){(void)ui;*frames=completed;*us=completed*1000;}
void esp_gsp_render_phases(esp_gsp_handle_t ui,uint64_t *raster,uint64_t *submit){(void)ui;*raster=completed*600;*submit=completed*400;}
const esp_app_desc_t *esp_app_get_description(void){static const esp_app_desc_t a={"host-status-fixture"};return &a;}
esp_err_t esp_iris_rpc_register(uint32_t service,uint16_t method,esp_iris_rpc_fn fn,void *ctx){assert(service==0x504c&&method==1&&fn==rpc&&!ctx);return ESP_OK;}
static void publish(peek_ui_t *v,unsigned at){completed++;device_status_publish(v,at);}
int main(void){
    peek_ui_t v={.ui=(void *)1,.sample_step=2};assert(device_status_start()==ESP_OK);
    publish(&v,100); /* Idle completed. */
    v.dragon.target_active=true;publish(&v,200); /* Still classify previous idle. */
    publish(&v,300); /* Previous active open. */
    v.dragon.pose.blink=.5f;publish(&v,400); /* Previous open, next closing. */
    v.dragon.pose.blink=1;v.dragon.sleeping=true;publish(&v,500);
    v.dragon.pose.blink=0;v.dragon.sleeping=false;publish(&v,600); /* Previous asleep excluded. */
    v.orientation=270;v.orientation_auto=true;v.orientation_error=ESP_FAIL;v.orientation_sampled_ms=650;
    publish(&v,700);
    assert(snapshot.open_frames==3 && snapshot.open_elapsed_ms==300);
    assert(snapshot.open_busy_us==3000 && snapshot.open_raster_us==1800 && snapshot.open_submit_us==1200);
    uint8_t out[2048];size_t n=0;esp_iris_rpc_request_t q={0};struct snapshot before=snapshot;
    assert(rpc(&q,out,sizeof(out),&n,NULL)==ESP_OK && n<sizeof(out));
    assert(strstr((char *)out,"\"open_frames\":3") && strstr((char *)out,"\"sleeping\":false"));
    assert(strstr((char *)out,"\"orientation\":270")&&strstr((char *)out,"\"imu_error\":-1"));
    assert(!memcmp(&snapshot,&before,sizeof(snapshot)));
    assert(rpc(&q,out,32,&n,NULL)==ESP_ERR_INVALID_SIZE);q.payload_size=1;assert(rpc(&q,out,sizeof(out),&n,NULL)==ESP_ERR_INVALID_ARG);
    v.dragon_view=true;
    for(unsigned character=1;character<=3;character++){
        v.character=character;publish(&v,700+100*character);
        assert(rpc(&q,out,sizeof(out),&n,NULL)==ESP_ERR_INVALID_ARG);q.payload_size=0;
        assert(rpc(&q,out,sizeof(out),&n,NULL)==ESP_OK);
        assert(strstr((char *)out,eye_pack_name(character-1)) && strstr((char *)out,"\"sample_step\":1"));
        q.payload_size=1;
    }
    q.payload_size=0;v.character=3;v.dragon.sleeping=true;v.dragon.pose.blink=1;v.dragon.pose.gaze_x=.6f;v.dragon.pose.gaze_y=-.4f;publish(&v,1200);
    assert(rpc(&q,out,sizeof(out),&n,NULL)==ESP_OK);
    assert(strstr((char *)out,"\"gaze_x\":0.60000")&&strstr((char *)out,"\"render_gaze_x\":0.00000")&&strstr((char *)out,"\"render_gaze_y\":0.00000"));
    puts("PASS device telemetry: previous generation classification, sleep/closing excluded, open timing exact,2048B body and RPC purity");
}

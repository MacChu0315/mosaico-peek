/* SPDX-License-Identifier: Apache-2.0 */
/* Compile the actual device adapter against deterministic scheduling/GSP stubs.
 * This proves Host behavior under adversarial ordering, not real hardware. */
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "peek_ui.h"
static unsigned freed,flushes,detached,deleted;
static int ui_failure,timer_failure,task_failure,flush_failure;
static bool queue_has_frame;
static int64_t fake_us;
static void *timer_context;
static void checked_free(void *p){if(p)freed++;free(p);}
#define free checked_free
#include "../projects/peek/main/device_thermal.c"
#undef free
const char *esp_err_to_name(esp_err_t e){(void)e;return "stub";}
int64_t esp_timer_get_time(void){return fake_us;}
QueueHandle_t xQueueCreate(unsigned n,size_t s){(void)n;(void)s;return (void *)1;}
void vQueueDelete(QueueHandle_t q){(void)q;}
int xQueueReceive(QueueHandle_t q,void *out,unsigned t){
    (void)q;(void)t;if(!queue_has_frame)return 0;queue_has_frame=false;
    /* Producer completes after a hypothetical pre-receive clock read. */
    fake_us=1002000;capture_t *m=out;memset(m,0,sizeof(*m));m->ok=true;m->sequence=1;m->ms=1001;
    for(unsigned i=0;i<768;i++)m->raw.pixels[i]=22;
    return pdTRUE;
}
int xQueueOverwrite(QueueHandle_t q,const void *m){(void)q;(void)m;return pdTRUE;}
int xTaskCreate(void (*fn)(void *),const char *n,unsigned stack,void *ctx,unsigned pri,void *out){(void)fn;(void)n;(void)stack;(void)ctx;(void)pri;(void)out;return task_failure?0:pdPASS;}
void vTaskDelay(unsigned ms){(void)ms;}
void vTaskDelete(void *p){(void)p;}
esp_err_t mosaico_module_mgr_init(void *c){(void)c;return ESP_OK;}
esp_err_t mosaico_module_mgr_claim(const mosaico_module_mgr_claim_config_t *c,mosaico_module_lease_t *l){(void)c;(void)l;return ESP_FAIL;}
esp_err_t mosaico_module_mgr_release(mosaico_module_lease_t *l){l->id=0;return ESP_OK;}
esp_err_t mosaico_thermal_new(bsp_subboard_slot_t s,const mosaico_thermal_config_t *c,mosaico_thermal_handle_t *h){(void)s;(void)c;(void)h;return ESP_FAIL;}
esp_err_t mosaico_thermal_read(mosaico_thermal_handle_t h,mosaico_thermal_frame_t *f,int t){(void)h;(void)f;(void)t;return ESP_FAIL;}
esp_err_t mosaico_thermal_del(mosaico_thermal_handle_t h){(void)h;return ESP_OK;}
esp_gsp_err_t peek_ui_init(peek_ui_t *s,esp_gsp_handle_t ui,peek_control_fn fn,void *ctx){memset(s,0,sizeof(*s));s->ui=ui;s->control=fn;s->context=ctx;assert(peek_init(&s->detector,NULL));return ui_failure?ESP_FAIL:ESP_OK;}
esp_gsp_err_t peek_ui_set_view(peek_ui_t *s,bool dragon){(void)s;(void)dragon;return ESP_GSP_OK;}
void peek_ui_release(peek_ui_t *s){(void)s;}
void peek_ui_reset(peek_ui_t *s,const char *name){(void)name;peek_reset(&s->detector);}
peek_submit_t peek_ui_submit(peek_ui_t *s,const peek_frame_t *f,uint64_t now){return peek_submit(&s->detector,f,now);}
void peek_ui_refresh(peek_ui_t *s,uint64_t now){assert(peek_tick(&s->detector,now));}
esp_gsp_err_t peek_ui_deinit(peek_ui_t *s){(void)s;detached++;return ESP_OK;}
void *esp_gsp_timer_create(esp_gsp_handle_t ui,uint32_t p,esp_gsp_timer_cb_t cb,void *ctx){(void)ui;(void)p;(void)cb;timer_context=ctx;return timer_failure?NULL:(void *)2;}
esp_gsp_err_t esp_gsp_timer_delete(esp_gsp_handle_t ui,void *timer){(void)ui;(void)timer;deleted++;return ESP_OK;}
esp_gsp_err_t esp_gsp_flush(esp_gsp_handle_t ui,uint32_t timeout){(void)ui;(void)timeout;assert(detached);assert(freed==0);flushes++;return flush_failure?ESP_FAIL:ESP_OK;}
static void reset_stubs(void){freed=flushes=detached=deleted=0;ui_failure=timer_failure=task_failure=flush_failure=0;timer_context=NULL;}
int main(void){
    reset_stubs();app=calloc(1,sizeof(*app));assert(peek_init(&app->view.detector,NULL));
    capture_t message={0};fake_us=1000000;queue_has_frame=true;refresh((void *)1,&message);
    assert(app->view.detector.result.accepted_samples==1 && app->view.detector.result.data==PEEK_VALID);
    free(app);app=NULL;
    for(unsigned failure=0;failure<3;failure++){
        reset_stubs();ui_failure=failure==0;timer_failure=failure==1;task_failure=failure==2;
        assert(device_thermal_start((void *)1)!=ESP_OK);
        assert(app==NULL && flushes==1 && detached==1 && freed==3);
        if(failure==2)assert(deleted==1);
    }
    reset_stubs();task_failure=flush_failure=1;
    assert(device_thermal_start((void *)1)!=ESP_OK);
    assert(app!=NULL && flushes==1 && freed==1); /* only unused producer freed */
    free(timer_context);free(app);app=NULL;
    puts("PASS device adapter: acquisition/clock interleaving, partial init teardown, failed flush retains contexts");
}

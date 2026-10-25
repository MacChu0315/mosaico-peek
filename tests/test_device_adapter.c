/* SPDX-License-Identifier: Apache-2.0 */
/* Compile the actual device adapter against deterministic scheduling/GSP stubs.
 * This proves Host behavior under adversarial ordering, not real hardware. */
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "peek_ui.h"
#ifndef TEST_DEVICE_MOUNT_FLIPS
#define TEST_DEVICE_MOUNT_FLIPS 0
#endif
static unsigned freed,flushes,detached,deleted;
static int fake_render_core,created_core;
static unsigned core_queries,waited_ms;
static void *producer_context;
static int ui_failure,timer_failure,task_failure,flush_failure;
static bool queue_has_frame;
static int64_t fake_us;
static void *timer_context;
static void checked_free(void *p){if(p)freed++;free(p);}
#define free checked_free
#define ESP_PLATFORM 1
#include "../projects/peek/main/device_thermal.c"
#undef ESP_PLATFORM
#undef free
const char *esp_err_to_name(esp_err_t e){(void)e;return "stub";}
int64_t esp_timer_get_time(void){return fake_us;}
QueueHandle_t xQueueCreate(unsigned n,size_t s){(void)n;(void)s;return (void *)1;}
void vQueueDelete(QueueHandle_t q){(void)q;}
int xQueueReceive(QueueHandle_t q,void *out,unsigned t){
    (void)q;(void)t;if(!queue_has_frame)return 0;queue_has_frame=false;
    /* Producer completes after a hypothetical pre-receive clock read. */
    fake_us=1002000;peek_live_t *m=out;assert(peek_live_init(m));
    if(producer_context)m->dragon.mapping=((producer_t *)producer_context)->live.dragon.mapping;
    peek_frame_t f={.sequence=1,.captured_ms=1001,.complete=true};
    for(unsigned i=0;i<768;i++){f.c[i]=22;f.valid[i]=1;}
    assert(peek_live_event(m,&f,false,1001));
    return pdTRUE;
}
int xQueueOverwrite(QueueHandle_t q,const void *m){(void)q;(void)m;return pdTRUE;}
int xTaskCreate(void (*fn)(void *),const char *n,unsigned stack,void *ctx,unsigned pri,void *out){(void)fn;(void)n;(void)stack;(void)ctx;(void)pri;(void)out;return task_failure?0:pdPASS;}
void vTaskDelay(unsigned ms){waited_ms+=ms;}
int device_status_render_core(void){core_queries++;return fake_render_core;}
void device_status_capture(bool ok){(void)ok;}
void device_status_publish(const peek_ui_t *s,uint64_t now){(void)s;(void)now;}
int xTaskCreatePinnedToCore(void (*fn)(void *),const char *n,unsigned stack,void *ctx,unsigned pri,void *out,int core){created_core=core;producer_context=ctx;assert(core==1-fake_render_core);return xTaskCreate(fn,n,stack,ctx,pri,out);}
void vTaskDelete(void *p){(void)p;}
esp_err_t mosaico_module_mgr_init(void *c){(void)c;return ESP_OK;}
esp_err_t mosaico_module_mgr_claim(const mosaico_module_mgr_claim_config_t *c,mosaico_module_lease_t *l){(void)c;(void)l;return ESP_FAIL;}
esp_err_t mosaico_module_mgr_release(mosaico_module_lease_t *l){l->id=0;return ESP_OK;}
esp_err_t mosaico_thermal_new(bsp_subboard_slot_t s,const mosaico_thermal_config_t *c,mosaico_thermal_handle_t *h){(void)s;(void)c;(void)h;return ESP_FAIL;}
esp_err_t mosaico_thermal_read(mosaico_thermal_handle_t h,mosaico_thermal_frame_t *f,int t){(void)h;(void)f;(void)t;return ESP_FAIL;}
esp_err_t mosaico_thermal_del(mosaico_thermal_handle_t h){(void)h;return ESP_OK;}
esp_gsp_err_t peek_ui_init(peek_ui_t *s,esp_gsp_handle_t ui,peek_control_fn fn,void *ctx){memset(s,0,sizeof(*s));s->ui=ui;s->control=fn;s->context=ctx;assert(peek_init(&s->detector,NULL));return ui_failure?ESP_FAIL:ESP_OK;}
esp_gsp_err_t peek_ui_set_view(peek_ui_t *s,bool dragon){(void)s;(void)dragon;return ESP_GSP_OK;}
esp_gsp_err_t peek_ui_set_character(peek_ui_t *s,unsigned character){(void)s;assert(character==0);return ESP_GSP_OK;}
void device_orientation_read(device_orientation_status_t *out){*out=(device_orientation_status_t){.rotation=90,.automatic=true};}
esp_gsp_err_t peek_ui_set_orientation(peek_ui_t *s,unsigned q){s->orientation=q;return ESP_GSP_OK;}
static uint32_t button_presses;static int button_delta;
uint32_t device_buttons_take_presses(void){uint32_t n=button_presses;button_presses=0;return n;}
esp_gsp_err_t peek_ui_cycle_character(peek_ui_t *s,int delta){button_delta=delta;s->character=peek_character_cycle(s->character,delta);return ESP_GSP_OK;}
void peek_ui_release(peek_ui_t *s){(void)s;}
void peek_ui_reset(peek_ui_t *s,const char *name){(void)name;peek_reset(&s->detector);}
peek_submit_t peek_ui_submit(peek_ui_t *s,const peek_frame_t *f,uint64_t now){return peek_submit(&s->detector,f,now);}
void peek_ui_refresh(peek_ui_t *s,uint64_t now){assert(peek_tick(&s->detector,now));}
esp_gsp_err_t peek_ui_deinit(peek_ui_t *s){(void)s;detached++;return ESP_OK;}
void *esp_gsp_timer_create(esp_gsp_handle_t ui,uint32_t p,esp_gsp_timer_cb_t cb,void *ctx){(void)ui;(void)p;(void)cb;timer_context=ctx;return timer_failure?NULL:(void *)2;}
esp_gsp_err_t esp_gsp_timer_delete(esp_gsp_handle_t ui,void *timer){(void)ui;(void)timer;deleted++;return ESP_OK;}
esp_gsp_err_t esp_gsp_flush(esp_gsp_handle_t ui,uint32_t timeout){(void)ui;(void)timeout;assert(detached);assert(freed==0);flushes++;return flush_failure?ESP_FAIL:ESP_OK;}
static void reset_stubs(void){freed=flushes=detached=deleted=0;ui_failure=timer_failure=task_failure=flush_failure=0;timer_context=NULL;producer_context=NULL;fake_render_core=0;created_core=-1;core_queries=waited_ms=0;}
int main(void){
    reset_stubs();app=calloc(1,sizeof(*app));assert(peek_init(&app->view.detector,NULL));
    peek_live_t message={0};fake_us=1000000;queue_has_frame=true;refresh((void *)1,&message);
    assert(app->view.detector.result.accepted_samples==1 && app->view.detector.result.data==PEEK_VALID);
    assert(app->view.orientation==90&&app->view.orientation_auto);
    button_presses=5;button_delta=0;refresh((void *)1,&message);
    assert(button_delta==2 && app->view.character==3 && !button_presses);
    free(app);app=NULL;
    for(unsigned failure=0;failure<3;failure++){
        reset_stubs();ui_failure=failure==0;timer_failure=failure==1;task_failure=failure==2;
        assert(device_thermal_start((void *)1)!=ESP_OK);
        assert(app==NULL && flushes==1 && detached==1 && freed==3);
        if(failure==2)assert(deleted==1);
    }
    for(int core=0;core<2;core++){
        reset_stubs();fake_render_core=core;
        assert(device_thermal_start((void *)1)==ESP_OK && created_core==1-core && core_queries==1);
        producer_t *p=producer_context;
        assert(p->live.dragon.mapping.flip_x==TEST_DEVICE_MOUNT_FLIPS && p->live.dragon.mapping.flip_y==TEST_DEVICE_MOUNT_FLIPS);
        assert(app->view.dragon.mapping.flip_x==TEST_DEVICE_MOUNT_FLIPS && app->view.dragon.mapping.flip_y==TEST_DEVICE_MOUNT_FLIPS);
        queue_has_frame=true;refresh((void *)1,timer_context);
        assert(app->view.dragon.mapping.flip_x==TEST_DEVICE_MOUNT_FLIPS && app->view.dragon.mapping.flip_y==TEST_DEVICE_MOUNT_FLIPS);
        float gx,gy;assert(dragon_map(&app->view.dragon.mapping,31,23,&gx,&gy));
        assert((gx<0)==TEST_DEVICE_MOUNT_FLIPS && (gy<0)==TEST_DEVICE_MOUNT_FLIPS);
        free(producer_context);free(timer_context);free(app);app=NULL;
    }
    reset_stubs();fake_render_core=-1;
    assert(device_thermal_start((void *)1)==ESP_ERR_TIMEOUT);
    assert(app==NULL && created_core==-1 && waited_ms==1000 && core_queries==100 && freed==3);
    reset_stubs();task_failure=flush_failure=1;
    assert(device_thermal_start((void *)1)!=ESP_OK);
    assert(app!=NULL && flushes==1 && freed==1); /* only unused producer freed */
    free(timer_context);free(app);app=NULL;
    puts("PASS device adapter: acquisition/clock interleaving, partial init teardown, failed flush retains contexts");
}

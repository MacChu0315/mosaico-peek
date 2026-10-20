#pragma once
#include "mosaico_module_mgr.h"
typedef void *mosaico_thermal_handle_t;
typedef struct {unsigned clock_speed_hz,refresh_rate;float emissivity,reflected_offset_c;} mosaico_thermal_config_t;
#define MOSAICO_THERMAL_DEFAULT_CONFIG() {400000,5,.95f,8}
typedef struct {float pixels[768],ambient_c,supply_v;} mosaico_thermal_frame_t;
esp_err_t mosaico_thermal_new(bsp_subboard_slot_t slot,const mosaico_thermal_config_t *cfg,mosaico_thermal_handle_t *sensor);
esp_err_t mosaico_thermal_read(mosaico_thermal_handle_t sensor,mosaico_thermal_frame_t *frame,int timeout);
esp_err_t mosaico_thermal_del(mosaico_thermal_handle_t sensor);

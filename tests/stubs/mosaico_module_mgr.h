#pragma once
#include "esp_err.h"
#define MOSAICO_BOARD_TYPE_THERMAL 0x12
#define MOSAICO_MODULE_MGR_SLOT_AUTO 2
typedef int bsp_subboard_slot_t;
typedef struct {unsigned slot,id;} mosaico_module_lease_t;
typedef struct {unsigned expected_type,slot,timeout_ms,flags;} mosaico_module_mgr_claim_config_t;
esp_err_t mosaico_module_mgr_init(void *config);
esp_err_t mosaico_module_mgr_claim(const mosaico_module_mgr_claim_config_t *cfg,mosaico_module_lease_t *lease);
esp_err_t mosaico_module_mgr_release(mosaico_module_lease_t *lease);

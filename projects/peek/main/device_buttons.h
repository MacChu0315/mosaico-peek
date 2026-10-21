/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "esp_err.h"
#include <stdint.h>
esp_err_t device_buttons_start(void);
/* Single UI owner drains counts; the BSP callback never accesses UI/sensors. */
uint32_t device_buttons_take_presses(void);

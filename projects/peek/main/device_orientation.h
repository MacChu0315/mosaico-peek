/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "esp_err.h"
#include <stdbool.h>
#include <stdint.h>
typedef struct {
    unsigned rotation;
    bool automatic;
    esp_err_t error;
    uint64_t sampled_ms;
    uint32_t samples;
    float ax,ay,az;
} device_orientation_status_t;
esp_err_t device_orientation_start(void);
/* Nonblocking snapshot, safe on the GSP owner; never reads I2C there. */
void device_orientation_read(device_orientation_status_t *out);

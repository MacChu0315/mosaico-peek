/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "peek_ui.h"
esp_err_t device_status_start(void);
void device_status_capture(bool ok);
void device_status_publish(const peek_ui_t *view,uint64_t now_ms);

/* SPDX-License-Identifier: Apache-2.0 */
#include <assert.h>
#include <stdio.h>
#include "sdkconfig.h"
#undef CONFIG_PEEK_AUTO_ORIENTATION
#undef CONFIG_PEEK_FIXED_ORIENTATION
#define CONFIG_PEEK_FIXED_ORIENTATION 3
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(p) ((void)(p))
#define portEXIT_CRITICAL(p) ((void)(p))
#include "../projects/peek/main/device_orientation.c"
int main(void){
    assert(device_orientation_start()==ESP_OK);
    device_orientation_status_t s;device_orientation_read(&s);
    assert(!s.automatic&&s.rotation==270&&s.error==ESP_OK&&s.samples==0);
    /* No driver/task stubs: fixed mode must not reference/start the IMU. */
    assert(device_orientation_start()==ESP_ERR_INVALID_STATE);
    puts("PASS fixed orientation without any IMU/task dependency");
}

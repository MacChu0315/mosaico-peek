#pragma once
#include "esp_err.h"
typedef struct {int unused;} bsp_imu_config_t;
#define BSP_IMU_CONFIG_DEFAULT() {0}
esp_err_t bsp_imu_init(void);
esp_err_t bsp_imu_start(const bsp_imu_config_t *config);
esp_err_t bsp_imu_deinit(void);
esp_err_t bsp_imu_stop(void);
esp_err_t bsp_imu_get_accel(float *x,float *y,float *z);
esp_err_t bsp_imu_get_gyro(float *x,float *y,float *z);

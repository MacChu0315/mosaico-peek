#pragma once
#include "esp_err.h"
#include <stddef.h>
#include <stdint.h>
typedef struct {size_t payload_size;} esp_iris_rpc_request_t;
typedef esp_err_t (*esp_iris_rpc_fn)(const esp_iris_rpc_request_t *,uint8_t *,size_t,size_t *,void *);
esp_err_t esp_iris_rpc_register(uint32_t service,uint16_t method,esp_iris_rpc_fn fn,void *ctx);

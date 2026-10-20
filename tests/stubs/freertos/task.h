#pragma once
#include <stddef.h>
int xTaskCreate(void (*fn)(void *),const char *name,unsigned stack,void *ctx,unsigned priority,void *out);
void vTaskDelay(unsigned ms);
void vTaskDelete(void *task);

int xTaskCreatePinnedToCore(void (*fn)(void *),const char *name,unsigned stack,void *ctx,unsigned priority,void *out,int core);

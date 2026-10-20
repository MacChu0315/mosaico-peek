#pragma once
#include <stddef.h>
typedef void *QueueHandle_t;
QueueHandle_t xQueueCreate(unsigned count,size_t size);
int xQueueReceive(QueueHandle_t queue,void *value,unsigned timeout);
int xQueueOverwrite(QueueHandle_t queue,const void *value);
void vQueueDelete(QueueHandle_t queue);

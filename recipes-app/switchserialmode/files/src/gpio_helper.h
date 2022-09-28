#ifndef GPIOHELPER
#define GPIOHELPER

#include <stdint.h>

void gpio_set(const uint8_t *line_name, uint32_t value);
#endif

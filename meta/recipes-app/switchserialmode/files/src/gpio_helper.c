/*
 * Copyright (c) Siemens AG, 2019-2022
 *
 * Authors:
 *  Gao Nian <nian.gao@siemens.com>
 *  Chao Zeng <chao.zeng@siemens.com>
 *
 * This file is subject to the terms and conditions of the MIT License.  See
 * COPYING.MIT file in the top-level directory.
 */

#include <stdlib.h>
#include <stdio.h>
#include <gpiod.h>
#include <string.h>
#include "gpio_helper.h"

void gpio_set(const uint8_t *line_name, uint32_t value)
{
    struct gpiod_line *line;

    line = gpiod_line_find(line_name);
    if (!line) {
        printf("Unable to find GPIO line %s\n", line_name);
        return;
    }

    if (gpiod_line_request_output(line, "switchserialmode", value) < 0) {
        perror("gpiod_line_request_output");
    }

    gpiod_line_release(line);
    gpiod_line_close_chip(line);
}

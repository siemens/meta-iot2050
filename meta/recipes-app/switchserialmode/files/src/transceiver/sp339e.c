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
#include "switchserialmode.h"
#include "gpio_helper.h"

static void sp339e_set_mode(uint32_t mode0, uint32_t mode1)
{
    gpio_set("UART0-enable", 1);
    gpio_set("UART0-mode0", mode0);
    gpio_set("UART0-mode1", mode1);
}

static void sp339e_set_termination(uint8_t onoff)
{
    gpio_set("UART0-terminate", onoff);
}

static void sp339e_switch_mode(const uint8_t *mode)
{
    if (0 == strcasecmp(mode, "rs232"))
    {
        sp339e_set_mode(1, 0);
    }
    else if(0 == strcasecmp(mode, "rs485"))
    {
        sp339e_set_mode(0, 1);
    }
    else if(0 == strcasecmp(mode, "rs422"))
    {
        sp339e_set_mode(1, 1);
    }
}

transceiver_ops_t sp339e_ops = {
    .transceiver_set_termination = sp339e_set_termination,
    .transceiver_switch_mode = sp339e_switch_mode,
};

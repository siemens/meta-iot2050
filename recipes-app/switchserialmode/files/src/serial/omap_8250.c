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

#include <unistd.h>
#include <stdlib.h>
#include <termios.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <linux/serial.h>
#include <linux/types.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include "switchserialmode.h"


#define GET_UART_RTS_ACTIVE_LOGIC(flags)  (!((flags) & SER_RS485_RTS_ON_SEND))

typedef struct omap_8250 {
    struct serial_rs485 r485Conf;
    int32_t uartHandle;
    int8_t (*ttyuart_set_rs485conf)(struct omap_8250 *);
} omap_8250_ops_t;

omap_8250_ops_t omap_8250_ops;

static int8_t ttyuart_get_rs485conf(struct omap_8250 *ops)
{
    int32_t ret = ioctl(ops->uartHandle, TIOCGRS485, &(ops->r485Conf));
    if (ret < 0) {
        perror("Error");
        return ERROR;
    }

    return SUCCESS;
}

static int8_t ttyuart_set_rs485conf(struct omap_8250 *ops)
{
    int32_t ret = ioctl(ops->uartHandle, TIOCSRS485, ops->r485Conf);
    if (ret < 0) {
        perror("Error");
        return ERROR;
    }

    return SUCCESS;
}

static int8_t ttyuart_init(uint8_t *uartdev)
{
    int32_t fd = open(uartdev, O_RDWR);
    if (fd < 0) {
        printf("Open tty uart failed\n");
        return ERROR;
    }

    omap_8250_ops.uartHandle = fd;
    omap_8250_ops.ttyuart_set_rs485conf = ttyuart_set_rs485conf;

    if (SUCCESS != ttyuart_get_rs485conf(&omap_8250_ops)) {
        printf("Get configuration fail\n");
        return ERROR;
    }

    return SUCCESS;
}

static void ttyuart_release(void)
{
    /*write conf to the device*/
    if (SUCCESS != omap_8250_ops.ttyuart_set_rs485conf(&omap_8250_ops)) {
        printf("Set configuration fail\n");
    }

    close(omap_8250_ops.uartHandle);
}

static void ttyuart_print_mode(void)
{
    const uint8_t *mode = NULL;
    const uint8_t *activelogic = NULL;
    struct serial_rs485 rs485Conf = omap_8250_ops.r485Conf;

    if (!(rs485Conf.flags & SER_RS485_ENABLED)) {
        mode = "rs232";
        activelogic = "";
    }
    else {
        if (rs485Conf.flags & SER_RS485_RX_DURING_TX) {
            mode = "rs422";
            activelogic = "";
        }
        else {
            mode = "rs485";
            activelogic = GET_UART_RTS_ACTIVE_LOGIC(rs485Conf.flags) ? "active-logic(high)" \
                                                                        : "active-logic(low)";
        }
    }

    printf("%s %s\n", mode, activelogic);
}

static void ttyuart_switch_mode(uint8_t *mode)
{
    struct serial_rs485 *rs485Conf = (struct serial_rs485 *)&(omap_8250_ops.r485Conf);
    memset(rs485Conf, 0, sizeof(rs485Conf));
    /*
        The latest kernel has already handle these flags.Its could be deleted.
        For the previous compatability, keep this settings
    */
    rs485Conf->flags &= ~(SER_RS485_RTS_ON_SEND);
    rs485Conf->flags |= (SER_RS485_RTS_AFTER_SEND);

    if (0 == strcasecmp(mode, "rs485")) {
        rs485Conf->flags |= SER_RS485_ENABLED;
    }
    else if (0 == strcasecmp(mode, "rs422")) {
        rs485Conf->flags |= SER_RS485_ENABLED | SER_RS485_RX_DURING_TX;
    }
    else if (0 == strcasecmp(mode, "rs232")) {
        memset(rs485Conf, 0, sizeof(rs485Conf));
    }
}

static void ttyuart_set_rs485_hold_time(uint8_t holdtime)
{
    printf("Set RS485 hold time not supported\n");
}

static void ttyuart_set_rs485_setup_time(uint8_t holdtime)
{
    printf("Set RS485 setup time not supported\n");
}

serial_ops_t ttyuart_ops = {
    .devName = "/dev/ttyX30",
    .init = ttyuart_init,
    .rs485HoldTime = ttyuart_set_rs485_hold_time,
    .rs485SetupTime = ttyuart_set_rs485_setup_time,
    .setMode = ttyuart_switch_mode,
    .getMode = ttyuart_print_mode,
    .release = ttyuart_release,
};

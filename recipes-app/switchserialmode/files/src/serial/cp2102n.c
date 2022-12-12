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

#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <libusb-1.0/libusb.h>
#include <stdarg.h>
#include <assert.h>
#include "gpio_helper.h"
#include "switchserialmode.h"

#define MAIN_GPIO_CONTROL_1_INDEX      600
#define CP2102N_RS485_BIT              4
#define MAIN_GPIO_CONTROL_2_INDEX      601
#define CP2102N_RS485_LOGIC_BIT        0
#define CP2102N_RS485_SETUP_INDEX      669
#define CP2102N_RS485_HOLD_INDEX       671
#define MAIN_RESET_LATCH_P1_INDEX      587
#define CP2102N_GPIO2_RESET_LATH_BIT   5

#define CP2102N_MAX_CONFIG_LENGTH      0x02a6

#define IS_CP2102N_RS485PIN_RS485_MODE(config)    ((config)[MAIN_GPIO_CONTROL_1_INDEX] \
                                                            & (1 << CP2102N_RS485_BIT))
#define IS_CP2102N_RS485PIN_RS485_LOGIC(config)   (config[MAIN_GPIO_CONTROL_2_INDEX] \
                                                            & (1 << CP2102N_RS485_LOGIC_BIT))
#define GET_CP2102N_GPIO2_RESET_LATH(config)   (config[MAIN_RESET_LATCH_P1_INDEX] \
                                                            & (uint8_t)(1 << CP2102N_GPIO2_RESET_LATH_BIT))
#define GET_CP2102N_RS485_SETUP_TIME(config)   (((config[CP2102N_RS485_SETUP_INDEX] << 8) & 0xff00)\
                                                            | (config[CP2102N_RS485_SETUP_INDEX + 1] & 0xff))
#define GET_CP2102N_RS485_HOLD_TIME(config)   (((config[CP2102N_RS485_HOLD_INDEX] << 8) & 0xff00) \
                                                            | (config[CP2102N_RS485_HOLD_INDEX + 1] & 0xff))

typedef struct cp2102n_conf_ops {
    uint8_t deviceConf[CP2102N_MAX_CONFIG_LENGTH];
    uint16_t confCheckSum;
    libusb_device_handle *usbHandle;
    /*cfg update function*/
    void (*cfg_rs485_setup_time)(struct cp2102n_conf_ops *conf, uint32_t timeVal);
    void (*cfg_rs485_hold_time)(struct cp2102n_conf_ops *conf, uint32_t timeVal);
    void (*cfg_rs485pin_to_gpio)(struct cp2102n_conf_ops *conf);
    void (*cfg_rs485pin_to_rs485)(struct cp2102n_conf_ops *conf);
    void (*cfg_rs485_logic)(struct cp2102n_conf_ops *conf, uint8_t logic);
    void (*cfg_rs485pin_gpio_reset_level)(struct cp2102n_conf_ops *conf, uint8_t rstLogic);
} cp2102n_conf_ops_t;

static cp2102n_conf_ops_t *cp2102n_cfg_operation = NULL;

static void cfg_cp2102n_rs485_setup_time(struct cp2102n_conf_ops *conf, uint32_t timeVal)
{
    conf->deviceConf[CP2102N_RS485_SETUP_INDEX] = (uint8_t)(((timeVal) >> 8) & 0xff);
    conf->deviceConf[CP2102N_RS485_SETUP_INDEX + 1] = (uint8_t)((timeVal) & 0xff);
}

static void cfg_cp2102n_rs485_hold_time(struct cp2102n_conf_ops *conf, uint32_t timeVal)
{
    conf->deviceConf[CP2102N_RS485_HOLD_INDEX] = (uint8_t)(((timeVal) >> 8) & 0xff);
    conf->deviceConf[CP2102N_RS485_HOLD_INDEX + 1] = (uint8_t)((timeVal) & 0xff);
}

static void cfg_cp2102n_rs485pin_to_gpio(struct cp2102n_conf_ops *conf)
{
    conf->deviceConf[MAIN_GPIO_CONTROL_1_INDEX] &= (uint8_t)(~(1 << CP2102N_RS485_BIT));
}

static void cfg_cp2102n_rs485pin_to_rs485(struct cp2102n_conf_ops *conf)
{
    conf->deviceConf[MAIN_GPIO_CONTROL_1_INDEX] |= (uint8_t)(1 << CP2102N_RS485_BIT);
}

static void cfg_cp2102n_rs485_logic(struct cp2102n_conf_ops *conf, uint8_t logic)
{
    if (logic)
        conf->deviceConf[MAIN_GPIO_CONTROL_2_INDEX] |= (uint8_t)(1 << CP2102N_RS485_LOGIC_BIT);
    else
        conf->deviceConf[MAIN_GPIO_CONTROL_2_INDEX] &= (uint8_t)(~(1 << CP2102N_RS485_LOGIC_BIT));
}

static void cfg_cp2102n_rs485pin_gpio_reset_level(struct cp2102n_conf_ops *conf, uint8_t rstLogic)
{
    if(rstLogic)
        conf->deviceConf[MAIN_RESET_LATCH_P1_INDEX] |= (uint8_t)(1 << CP2102N_GPIO2_RESET_LATH_BIT);
    else
        conf->deviceConf[MAIN_RESET_LATCH_P1_INDEX] &= (uint8_t)(~(1 << CP2102N_GPIO2_RESET_LATH_BIT));
}

static int8_t cp2102n_read_config(struct cp2102n_conf_ops *conf)
{
    assert(conf->usbHandle);
    uint32_t rlen = libusb_control_transfer(conf->usbHandle, 0xC0, 0xFF,
                                            0x0E, /* wValue */
                                            0, /* WIndex */
                                            conf->deviceConf, /* data */
                                            CP2102N_MAX_CONFIG_LENGTH, /* data size */
                                            0);

    return (rlen == CP2102N_MAX_CONFIG_LENGTH) ? SUCCESS : ERROR;
}

static int8_t cp2102n_write_config_to_device(struct cp2102n_conf_ops *conf)
{
    assert(conf->usbHandle);
    uint32_t wlen = libusb_control_transfer(conf->usbHandle, 0x40, 0xFF,
                                            0x370F, /* wValue */
                                            0, /* WIndex */
                                            conf->deviceConf, /* data */
                                            CP2102N_MAX_CONFIG_LENGTH, /* data size */
                                            0);

    return (wlen == CP2102N_MAX_CONFIG_LENGTH) ? SUCCESS : ERROR;
}

static int8_t find_on_board_cp2102n(libusb_device *device)
{
    /*
        On iot2050 board cp2102n locate at 1.4
     */
    #define ROOT_HUB_PORT 1
    #define INTERMINATE_HUB_PORT 4
    uint8_t port_numbers[7];

    int r = libusb_get_port_numbers(device, port_numbers, 7);
    if (r != 2)
        return ERROR;

    if ((ROOT_HUB_PORT == port_numbers[0]) &&
        INTERMINATE_HUB_PORT == port_numbers[1]) {
        return SUCCESS;
    }

    printf("No matched cp2102n\n");
    return ERROR;
}

static int8_t cp2102n_open(struct cp2102n_conf_ops *conf)
{
    libusb_device **list = NULL;
    libusb_device *found = NULL;

    const uint8_t numOfUSBDevices = libusb_get_device_list(NULL, &list);

    if (numOfUSBDevices < 0) {
        printf("Libusb_get_device_list error");
        goto error;
    }

    for (uint8_t i = 0; i < numOfUSBDevices; i++) {
        if (!find_on_board_cp2102n(list[i])) {
            found = list[i];
            break;
        }
    }

    if (found) {
        if (libusb_open(found, &(conf->usbHandle))) {
            printf("Open usb failed\n");
            goto error;
        }
    } else {
        printf("No matched device found\n");
        goto error;
    }

    libusb_free_device_list(list, 1);
    return SUCCESS;

error:
    libusb_free_device_list(list, 1);
    return ERROR;

}

static void cp2102n_close(struct cp2102n_conf_ops *conf)
{
    if(NULL != conf->usbHandle) {
        libusb_close(conf->usbHandle);
    }
}

/* cp210x checksum caculate method */
static uint16_t fletcher16(const uint8_t *bytes, uint16_t len)
{
    uint16_t sum1 = 0xff, sum2 = 0xff;
    uint16_t tlen = 0;

    while (len) {
        tlen = len >= 20 ? 20 : len;
        len -= tlen;
        do {
                sum2 += sum1 += *bytes++;
        } while (--tlen);
        sum1 = (sum1 & 0xff) + (sum1 >> 8);
        sum2 = (sum2 & 0xff) + (sum2 >> 8);
    }
    /* Second reduction step to reduce sums to 8 bits */
    sum1 = (sum1 & 0xff) + (sum1 >> 8);
    sum2 = (sum2 & 0xff) + (sum2 >> 8);
    return sum2 << 8 | sum1;
}

static int8_t write_config_to_device(struct cp2102n_conf_ops *conf)
{
    uint16_t checkSumNew = fletcher16(conf -> deviceConf, CP2102N_MAX_CONFIG_LENGTH - 2);
    uint8_t deviceConf[CP2102N_MAX_CONFIG_LENGTH] = {0};
    if (conf -> confCheckSum != checkSumNew) {
        //update checksum
        conf->deviceConf[CP2102N_MAX_CONFIG_LENGTH - 2] = (uint8_t)((checkSumNew >> 8) & 0xff);
        conf->deviceConf[CP2102N_MAX_CONFIG_LENGTH - 1] = (uint8_t)((checkSumNew) & 0xff);
        if(SUCCESS != cp2102n_write_config_to_device(conf)) {
            printf("cp2102n_write_config_to_device failed\n");
            return ERROR;
        }

        memcpy(deviceConf, conf->deviceConf, CP2102N_MAX_CONFIG_LENGTH);
        cp2102n_read_config(conf);
        if (memcmp(deviceConf, conf->deviceConf, CP2102N_MAX_CONFIG_LENGTH)) {
            printf("Write configuration failed\n");
            return ERROR;
        }
    }
    return SUCCESS;
} 

static void cp2102n_hardware_reset(void)
{
    /*
        reset device to take effective right now
        for pg1 advanced board,there is no wire connect to reset pin.reset would not work.
        for later baord, hardware reset can take effective.
    */
    if (ADVANCED_BOARD_PG1 != get_board_type()) {
        gpio_set("CP2102N-RESET", 0);
        usleep(30 * 1000);
        gpio_set("CP2102N-RESET", 1);
        sleep(1);
    }
}

static void cp2102n_set_rs485_setup_time(uint8_t setuptime)
{
    cp2102n_cfg_operation->cfg_rs485_setup_time(cp2102n_cfg_operation, setuptime);
}

static void cp2102n_set_rs485_hold_time(uint8_t holdtime)
{
    cp2102n_cfg_operation->cfg_rs485_hold_time(cp2102n_cfg_operation, holdtime);
}

static void print_cfg(uint8_t *devConf)
{
    const uint8_t *mode = NULL;
    const uint8_t *activeLogic = NULL;

    if (IS_CP2102N_RS485PIN_RS485_MODE((devConf))) {
        mode = "rs485";
        activeLogic = IS_CP2102N_RS485PIN_RS485_LOGIC(devConf) ? "high" : "low";
    }
    else {
        if (GET_CP2102N_GPIO2_RESET_LATH(devConf)) {
            mode = "rs422";
            activeLogic = "high";
        }
        else {
            mode = "rs232";
            activeLogic = "low";
        }
    }

    printf("%s %s setup-time(0x%04x) hold-time(0x%04x)\n",
            mode, activeLogic,
            GET_CP2102N_RS485_SETUP_TIME(devConf),
            GET_CP2102N_RS485_HOLD_TIME(devConf));
}

static void cp2102n_print_mode(void)
{
    print_cfg(cp2102n_cfg_operation->deviceConf);
}

static void cp2102n_switch_mode(uint8_t *mode)
{
    if (0 == strcasecmp(mode, "rs232")) {
        cp2102n_cfg_operation->cfg_rs485pin_to_gpio(cp2102n_cfg_operation);
        cp2102n_cfg_operation->cfg_rs485pin_gpio_reset_level(cp2102n_cfg_operation, 0);
    }
    else if (0 == strcasecmp(mode, "rs422")) {
        cp2102n_cfg_operation->cfg_rs485pin_to_gpio(cp2102n_cfg_operation);
        cp2102n_cfg_operation->cfg_rs485pin_gpio_reset_level(cp2102n_cfg_operation, 1);
    }
    else if(0 == strcasecmp(mode, "rs485")) {
        cp2102n_cfg_operation->cfg_rs485pin_to_rs485(cp2102n_cfg_operation);
        cp2102n_cfg_operation->cfg_rs485_logic(cp2102n_cfg_operation, 1);
    }
}

static int8_t cp2102_ops_init(struct cp2102n_conf_ops **conf)
{
    if (cp2102n_open(*conf)) {
        printf("Open usb device failed\n");
        return ERROR;
    }

    if (cp2102n_read_config(*conf)) {
        printf("Read config failed\n");
        return ERROR;
    }

    (*conf)->confCheckSum = fletcher16((*conf)->deviceConf, CP2102N_MAX_CONFIG_LENGTH - 2);
    (*conf)->cfg_rs485_setup_time = cfg_cp2102n_rs485_setup_time;
    (*conf)->cfg_rs485_hold_time = cfg_cp2102n_rs485_hold_time;
    (*conf)->cfg_rs485_logic = cfg_cp2102n_rs485_logic;
    (*conf)->cfg_rs485pin_gpio_reset_level = cfg_cp2102n_rs485pin_gpio_reset_level;
    (*conf)->cfg_rs485pin_to_gpio = cfg_cp2102n_rs485pin_to_gpio;
    (*conf)->cfg_rs485pin_to_rs485 = cfg_cp2102n_rs485pin_to_rs485;

    return SUCCESS;
}

static int8_t cp2102n_init(uint8_t *deviceNode)
{
    libusb_init(NULL);

    cp2102n_cfg_operation = (cp2102n_conf_ops_t *)malloc(sizeof(cp2102n_conf_ops_t));
    memset(cp2102n_cfg_operation, 0, sizeof(cp2102n_conf_ops_t));

    if (cp2102_ops_init(&cp2102n_cfg_operation)) {
        printf("Cp2102n init falied\n");
        return ERROR;
    }

    return SUCCESS;
}

static void cp2102n_release()
{
    int8_t ret = write_config_to_device(cp2102n_cfg_operation);
    cp2102n_close(cp2102n_cfg_operation);
    free(cp2102n_cfg_operation);
    cp2102n_cfg_operation = NULL;
    libusb_exit(NULL);
    if (SUCCESS == ret)
        cp2102n_hardware_reset();
}

static void cp2102n_pre_process(void *data)
{
    platform_t *preProcess = (platform_t *)data;
    if (preProcess->private_data) {
        controller_setting_t *privData = (controller_setting_t *)(preProcess->private_data);
        if ((0 == GET_CP2102N_RS485_SETUP_TIME(cp2102n_cfg_operation->deviceConf)) ||
            (0 == GET_CP2102N_RS485_HOLD_TIME(cp2102n_cfg_operation->deviceConf))) {
            cfg_cp2102n_rs485_setup_time(cp2102n_cfg_operation, privData->setup_time);
            cfg_cp2102n_rs485_hold_time(cp2102n_cfg_operation, privData->hold_time);
        }
    }
}

serial_ops_t cp210x_ops = {
    .devName = "cp2102n24",
    .init = cp2102n_init,
    .setMode = cp2102n_switch_mode,
    .getMode = cp2102n_print_mode,
    .rs485HoldTime = cp2102n_set_rs485_hold_time,
    .rs485SetupTime = cp2102n_set_rs485_setup_time,
    .release = cp2102n_release,
    .preProcess = cp2102n_pre_process,
};

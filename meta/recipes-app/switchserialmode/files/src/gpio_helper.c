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
#ifdef LIB_GPIOD_V2_API
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
#endif
#include <stdlib.h>
#include <stdio.h>
#include <gpiod.h>
#include <string.h>
#include "gpio_helper.h"

#ifdef LIB_GPIOD_V2_API
int is_gpio_chip_dir(const struct dirent* entry)
{
    struct stat statbuf;
    char path[300];

    snprintf(path, sizeof(path), "/dev/%s", entry->d_name);
    if (stat(path, &statbuf) < 0)
        return 0;

    // gpio chip device should not be a symlink
    if (S_ISLNK(statbuf.st_mode))
        return 0;

    return (gpiod_is_gpiochip_device(path) ? 1 : 0);
}

#define FREE_SCANDIR_MEM(num, mem)     \
    do {                               \
        int _i;                        \
        for (_i = 0; _i < num; _i++) { \
            free(mem[_i]);             \
        }                              \
        free(mem);                     \
    } while (0U)

#endif

void gpio_set(const uint8_t* line_name, uint32_t value)
{
#ifdef LIB_GPIOD_V2_API
    struct gpiod_chip* chip = NULL;
    struct gpiod_line_request* request = NULL;
    struct gpiod_line_settings* settings = NULL;
    struct gpiod_line_config* line_cfg = NULL;
    struct gpiod_request_config* req_cfg = NULL;
    bool success = false;
    int num_chips, i, line_offset;
    struct dirent** namelist;
    char path[300];
    num_chips = scandir("/dev", &namelist, is_gpio_chip_dir, versionsort);
    if (num_chips < 0) {
        perror("Cannot find GPIO chips.\n");
        FREE_SCANDIR_MEM(num_chips, namelist);
        return;
    }
    for (i = 0; i < num_chips; i++) {
        snprintf(path, sizeof(path), "/dev/%s", namelist[i]->d_name);
        chip = gpiod_chip_open(path);
        if (!chip) {
            continue;
        }
        line_offset = gpiod_chip_get_line_offset_from_name(chip, line_name);
        if (line_offset < 0) {
            gpiod_chip_close(chip);
            continue;
        }
        settings = gpiod_line_settings_new();
        if (!settings) {
            perror("Failed to create line settings");
            break;
        }

        if (gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_OUTPUT)) {
            perror("Failed to set line direction");
            break;
        }

        if (gpiod_line_settings_set_output_value(settings, value == 0 ? GPIOD_LINE_VALUE_INACTIVE : GPIOD_LINE_VALUE_ACTIVE)) {
            perror("Failed to set line output value");
            break;
        }

        line_cfg = gpiod_line_config_new();
        if (!line_cfg) {
            perror("Failed to create line config");
            break;
        }
        if (gpiod_line_config_add_line_settings(line_cfg, &line_offset, 1, settings) < 0) {
            perror("Failed to add line settings to config");
            break;
        }
        req_cfg = gpiod_request_config_new();
        if (!req_cfg) {
            perror("Failed to create request config");
            break;
        }
        gpiod_request_config_set_consumer(req_cfg, "switchserialmode");
        request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);
        if (!request) {
            perror("Failed to request line");
            break;
        }
        success = true;
        break;
    }
    if (success == false)
        fprintf(stderr, "Cannot find GPIO line %s", line_name);

    if (request)
        gpiod_line_request_release(request);
    if (req_cfg)
        gpiod_request_config_free(req_cfg);
    if (line_cfg)
        gpiod_line_config_free(line_cfg);
    if (settings)
        gpiod_line_settings_free(settings);

    if (chip)
        gpiod_chip_close(chip);
    FREE_SCANDIR_MEM(num_chips, namelist);
}
#else
void gpio_set(const uint8_t* line_name, uint32_t value)
{
    struct gpiod_line* line;

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
#endif

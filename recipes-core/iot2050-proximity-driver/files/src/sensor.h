/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: Copyright (c) Siemens AG, 2025
 * SPDX-FileContributor: Authored by Su Bao Cheng <baocheng.su@siemens.com>
 */

#ifndef IOT2050_PXMTD_SENSOR_H
#define IOT2050_PXMTD_SENSOR_H

#include <stdint.h>

int init_sensor();
int retrieve_sensor_data(uint16_t *ps_val);

#endif /* IOT2050_PXMTD_SENSOR_H */

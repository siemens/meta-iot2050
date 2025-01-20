/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: Copyright (c) Siemens AG, 2025
 * SPDX-FileContributor: Authored by Su Bao Cheng <baocheng.su@siemens.com>
 */

#ifndef IOT2050_PXMTD_DBUS_SERVICE_H
#define IOT2050_PXMTD_DBUS_SERVICE_H

#include <stdint.h>

typedef int (*retrieve_callback_t)(uint16_t *);

int dbus_serve(retrieve_callback_t cb);

#endif /* IOT2050_PXMTD_DBUS_SERVICE_H */

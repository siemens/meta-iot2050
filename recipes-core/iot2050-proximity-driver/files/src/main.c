/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: Copyright (c) Siemens AG, 2025
 * SPDX-FileContributor: Authored by Su Bao Cheng <baocheng.su@siemens.com>
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "sensor.h"
#include "dbus-service.h"

int main()
{
	setbuf(stdout, NULL);

	int ret = init_sensor();
	if (ret < 0) {
		fprintf(stderr, "Failed to initialize the sensor: %s\n",
			strerror(-ret));
		exit(EXIT_FAILURE);
	}

	return dbus_serve(retrieve_sensor_data) == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}

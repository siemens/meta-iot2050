/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: Copyright (c) Siemens AG, 2025
 * SPDX-FileContributor: Authored by Su Bao Cheng <baocheng.su@siemens.com>
 */

#include <systemd/sd-bus.h>
#include <errno.h>
#include <sys/capability.h>
#include "dbus-service.h"

typedef int (*retrieve_callback_t)(uint16_t *);

static retrieve_callback_t iot2050_pxmtd_retrieve_cb = NULL;

static int iot2050_pxmtd_retrieve(sd_bus_message *m,
				  void *userdata,
				  sd_bus_error *ret_error)
{
	if (!iot2050_pxmtd_retrieve_cb)
		return -ENXIO;

	uint16_t ps_val;
	int ret = iot2050_pxmtd_retrieve_cb(&ps_val);
	if (ret < 0)
		return ret;

	return sd_bus_reply_method_return(m, "q", ps_val);
}

static const sd_bus_vtable iot2050_pxmtd_vtable[] = {
	SD_BUS_VTABLE_START(0),
	SD_BUS_METHOD("Retrieve",
		      SD_BUS_NO_ARGS,
		      "q",
		      iot2050_pxmtd_retrieve,
		      SD_BUS_VTABLE_UNPRIVILEGED),
	SD_BUS_VTABLE_END
};

int dbus_serve(retrieve_callback_t cb)
{
	sd_bus_slot *slot = NULL;
	sd_bus *bus = NULL;
	int ret;

	ret = sd_bus_open_system(&bus);
	if (ret < 0) {
		fprintf(stderr, "Failed to connect to system bus: %s\n",
			strerror(-ret));
		goto out;
	}

	iot2050_pxmtd_retrieve_cb = cb;

	ret = sd_bus_add_object_vtable(bus, &slot,
				       "/com/siemens/iot2050/pxmt",
				       "com.siemens.iot2050.pxmt",
				       iot2050_pxmtd_vtable, NULL);
	if (ret < 0) {
		fprintf(stderr, "Failed to set dbus service property: %s\n",
			strerror(-ret));
		goto out;
	}

        ret = sd_bus_request_name(bus, "com.siemens.iot2050.pxmt", 0);
        if (ret < 0) {
                fprintf(stderr, "Failed to acquire service name: %s\n",
			strerror(-ret));
                goto out;
        }

        for (;;) {
                ret = sd_bus_process(bus, NULL);
                if (ret < 0) {
                        fprintf(stderr, "Failed to process bus: %s\n",
				strerror(-ret));
                        goto out;
                }
                if (ret > 0)
                        continue;

                ret = sd_bus_wait(bus, (uint64_t) -1);
                if (ret < 0) {
                        fprintf(stderr, "Failed to wait on bus: %s\n",
				strerror(-ret));
                        goto out;
                }
        }

	ret = 0;
out:
	sd_bus_slot_unref(slot);
	sd_bus_unref(bus);

	return ret;
}

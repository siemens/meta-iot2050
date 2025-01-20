# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright (c) Siemens AG, 2025
# SPDX-FileContributor: Authored by Su Bao Cheng <baocheng.su@siemens.com>

CROSS_COMPILE ?= aarch64-linux-gnu-

CC = $(CROSS_COMPILE)gcc

LDFLAGS = -lsystemd

TARGET = iot2050-pxmtd

INSTALL ?= install

DESTDIR ?= /

SRC = main.c \
	dbus-service.c \
	sensor.c

.PHONY: all clean install

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET)

install:
	$(INSTALL) -v -d $(DESTDIR)/usr/bin
	$(INSTALL) -v -d $(DESTDIR)/etc/dbus-1/system.d
	$(INSTALL) -v -m 0755 $(TARGET) $(DESTDIR)/usr/bin
	$(INSTALL) -v -m 0644 com.siemens.iot2050.pxmt.conf \
		$(DESTDIR)/etc/dbus-1/system.d
	$(INSTALL) -v -d ${DESTDIR}/lib/systemd/system/
	$(INSTALL) -v -m 0644 iot2050-proximity-driver.service\
		${DESTDIR}/lib/systemd/system/

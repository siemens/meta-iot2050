/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: Copyright (c) Siemens AG, 2025
 * SPDX-FileContributor: Authored by Su Bao Cheng <baocheng.su@siemens.com>
 */

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include "sensor.h"

#define I2C_BUS				"/dev/i2c-5"
#define I2C_SLAVE_ADDR			0x44

#define REG_OP_MODE_SEL			0x00
#define REG_PS_SETTING			0x0A
#define REG_LED_PULSE_SETTING		0x0C
#define REG_DATA_LSB			0x11
#define REG_DATA_MSB			0x12
#define REG_PS_SETTING_2		0x13
#define REG_PS_OFFSET_CANCEL_LSB	0x14
#define REG_PS_OFFSET_CANCEL_MSB	0x15
#define REG_DEV_ID			0x18

#define DEV_ID_PM16D17			0x11

#define PS_ENABLE_SHIFT			3
#define PS_ENABLE_MASK			0x01

#define PS_GAIN_SHIFT			6
#define PS_GAIN_MASK			0x03

#define INT_TIME_SHIFT			3
#define INT_TIME_MASK			0x07

#define WAIT_TIME_SHIFT			0
#define WAIT_TIME_MASK			0x07

#define OFFSET_CANCEL_SHIFT		7
#define OFFSET_CANCEL_MASK		0x01

#define PS_GAIN_X1			0
#define PS_GAIN_X2			1
#define PS_GAIN_X4			2
#define PS_GAIN_X8			3

#define INT_TIME_0_4_MS			0
#define INT_TIME_0_8_MS			1
#define INT_TIME_1_6_MS			2
#define INT_TIME_3_2_MS			3
#define INT_TIME_6_3_MS			4
#define INT_TIME_12_6_MS		5
#define INT_TIME_25_2_MS		6
#define INT_TIME_25_2_MS_2		7

#define WAIT_TIME_12_5_MS		0
#define WAIT_TIME_25_MS			1
#define WAIT_TIME_50_MS			2
#define WAIT_TIME_100_MS		3
#define WAIT_TIME_200_MS		4
#define WAIT_TIME_400_MS		5
#define WAIT_TIME_800_MS		6
#define WAIT_TIME_1600_MS		7

#define GET_FIELD_VALUE(reg, shift, mask)	\
	(((reg) >> (shift)) & (mask))

#define SET_FIELD_VALUE(val, shift, mask)	\
	(((val) & (mask)) << (shift))

static int i2c_prepare_bus(int *i2c_bus)
{
	int fbus = -1;
	int ret = 0;

	fbus = open(I2C_BUS, O_RDWR);
	if (fbus == -1) {
		ret = -errno;
		fprintf(stderr, "Failed to open the I2C bus: %s\n",
			strerror(-ret));
		goto fail;
	}

	if (ioctl(fbus, I2C_SLAVE, I2C_SLAVE_ADDR) == -1) {
		ret = -errno;
		fprintf(stderr,
			"Failed to specify the I2C bus slave address: %s\n",
			strerror(-ret));
		goto fail;
	}

	*i2c_bus = fbus;
	return 0;
fail:
	if (fbus > 0) close(fbus);
	return ret;
}

static int i2c_read_byte(int i2c_bus, uint8_t reg, uint8_t *val)
{
	int ret = 0;

	if (write(i2c_bus, &reg, 1) != 1) {
		ret = -errno;
		fprintf(stderr,
			"Failed to write I2C reg address 0x%02X: %s\n",
			reg, strerror(-ret));
		goto out;
	}

	if (read(i2c_bus, val, 1) != 1) {
		ret = -errno;
		fprintf(stderr,
			"Failed to read I2C reg 0x%02X value: %s\n",
			reg, strerror(-ret));
		goto out;
	}
out:
	return ret;
}
static int i2c_read_word(int i2c_bus,
			 uint8_t reg_lsb,
			 uint8_t reg_msb,
			 uint16_t *val)
{
	uint8_t lsb, msb;
	int ret;

	ret = i2c_read_byte(i2c_bus, reg_lsb, &lsb);
	if (ret != 0)
		goto out;

	ret = i2c_read_byte(i2c_bus, reg_msb, &msb);
	if (ret != 0)
		goto out;

	*val = (msb << 8) | lsb;
out:
	return ret;
}

static int i2c_write_byte(int i2c_bus, uint8_t reg, uint8_t val)
{
	int ret = 0;
	uint8_t buffer[2] = {reg, val};

	if (write(i2c_bus, buffer, 2) != 2) {
		ret = -errno;
		fprintf(stderr,
			"Failed to write I2C reg 0x%02X value 0x%02X: %s\n",
			reg, val, strerror(-ret));
		goto out;
	}
out:
	return ret;
}

static const char* dump_ps_gain(uint8_t ps_setting)
{
	uint8_t ps_gain = GET_FIELD_VALUE(ps_setting,
					  PS_GAIN_SHIFT,
					  PS_GAIN_MASK);
	switch (ps_gain) {
	case PS_GAIN_X1:
		return "X1";
	case PS_GAIN_X2:
		return "X2";
	case PS_GAIN_X4:
		return "X4";
	case PS_GAIN_X8:
		return "X8";
	default:
		return "Unknown";
	}
}

static const char* dump_itime(uint8_t ps_setting)
{
	uint8_t itime = GET_FIELD_VALUE(ps_setting,
					INT_TIME_SHIFT,
					INT_TIME_MASK);

	switch (itime) {
	case INT_TIME_0_4_MS:
		return "0.4 ms";
	case INT_TIME_0_8_MS:
		return "0.8 ms";
	case INT_TIME_1_6_MS:
		return "1.6 ms";
	case INT_TIME_3_2_MS:
		return "3.2 ms";
	case INT_TIME_6_3_MS:
		return "6.3 ms";
	case INT_TIME_12_6_MS:
		return "12.6 ms";
	case INT_TIME_25_2_MS:
	case INT_TIME_25_2_MS_2:
		return "25.2 ms";
	default:
		return "Unknown";
	}
}

static const char* dump_resolution(uint8_t ps_setting)
{
	uint8_t itime = GET_FIELD_VALUE(ps_setting,
					INT_TIME_SHIFT,
					INT_TIME_MASK);
	switch (itime) {
	case INT_TIME_0_4_MS:
		return "10 b";
	case INT_TIME_0_8_MS:
		return "11 b";
	case INT_TIME_1_6_MS:
		return "12 b";
	case INT_TIME_3_2_MS:
		return "13 b";
	case INT_TIME_6_3_MS:
		return "14 b";
	case INT_TIME_12_6_MS:
		return "15 b";
	case INT_TIME_25_2_MS:
	case INT_TIME_25_2_MS_2:
		return "16 b";
	default:
		return "Unknown";
	}
}

static const char* dump_wtime(uint8_t ps_setting)
{
	uint8_t wtime = GET_FIELD_VALUE(ps_setting,
					WAIT_TIME_SHIFT,
					WAIT_TIME_MASK);
	switch (wtime) {
	case WAIT_TIME_12_5_MS:
		return "12.5 ms";
	case WAIT_TIME_25_MS:
		return "25 ms";
	case WAIT_TIME_50_MS:
		return "50 ms";
	case WAIT_TIME_100_MS:
		return "100 ms";
	case WAIT_TIME_200_MS:
		return "200 ms";
	case WAIT_TIME_400_MS:
		return "400 ms";
	case WAIT_TIME_800_MS:
		return "800 ms";
	case WAIT_TIME_1600_MS:
		return "1600 ms";
	default:
		return "Unknown";
	}
}

static void dump_sensor_config(int i2c_bus)
{
	int ret;
	uint8_t op_mode;
	uint8_t ps_setting;
	uint8_t pulse_setting;
	uint8_t ps_setting_2;
	uint8_t ps_offset_cancel_lsb;
	uint8_t ps_offset_cancel_msb;
	uint16_t ps_offset_cancel;

	ret = i2c_read_byte(i2c_bus, REG_OP_MODE_SEL, &op_mode);
	ret || (ret = i2c_read_byte(i2c_bus,
				    REG_PS_SETTING,
				    &ps_setting));
	ret || (ret = i2c_read_byte(i2c_bus,
				    REG_LED_PULSE_SETTING,
				    &pulse_setting));
	ret || (ret = i2c_read_byte(i2c_bus,
				    REG_PS_SETTING_2,
				    &ps_setting_2));
	ret || (ret = i2c_read_byte(i2c_bus,
				    REG_PS_OFFSET_CANCEL_LSB,
				    &ps_offset_cancel_lsb));
	ret || (ret = i2c_read_byte(i2c_bus,
				    REG_PS_OFFSET_CANCEL_MSB,
				    &ps_offset_cancel_msb));
	ret || (ret = i2c_read_word(i2c_bus,
				    REG_PS_OFFSET_CANCEL_LSB,
				    REG_PS_OFFSET_CANCEL_MSB,
				    &ps_offset_cancel));

	if (ret != 0)
		return;

	uint8_t ps_en = GET_FIELD_VALUE(op_mode,
					PS_ENABLE_SHIFT,
					PS_ENABLE_MASK);
	uint8_t offset_cancel = GET_FIELD_VALUE(ps_setting_2,
						OFFSET_CANCEL_SHIFT,
						OFFSET_CANCEL_MASK);

	printf("0x00:OP_MODE_SEL:       0x%02X\n", op_mode);
	printf("  - PS Enabled:             %d\n", ps_en);
	printf("0x0A:PS_SETTING:        0x%02X\n", ps_setting);
	printf("  - PS Gain:                %s\n", dump_ps_gain(ps_setting));
	printf("  - ITIME:                  %s\n", dump_itime(ps_setting));
	printf("  - Resolution:             %s\n", dump_resolution(ps_setting));
	printf("  - WTIME:                  %s\n", dump_wtime(ps_setting));
	printf("0x0C:LED_PULSE_SETTING: 0x%02X\n", pulse_setting);
	printf("  - Pulse Count:            %d\n", (uint16_t)pulse_setting + 1);
	printf("0x13:PS_SETTING_2:      0x%02X\n", ps_setting_2);
	printf("  - Offset Cancel:          %d\n", offset_cancel);
	printf("0x14:OFFSET_CANCEL_LSB: 0x%02X\n", ps_offset_cancel_lsb);
	printf("0x15:OFFSET_CANCEL_MSB: 0x%02X\n", ps_offset_cancel_msb);
	printf("  - Offset Cancel Val:      %d\n", ps_offset_cancel);
	return;
}

int init_sensor()
{
	int i2c_bus = -1;
	int ret = 0;

	ret = i2c_prepare_bus(&i2c_bus);
	if (ret != 0)
		goto out;

	uint8_t id;
	ret = i2c_read_byte(i2c_bus, REG_DEV_ID, &id);
	if (ret != 0)
		goto out;

	if (id != DEV_ID_PM16D17) {
		fprintf(stderr, "Device ID mismatch: 0x%02X\n", id);
		ret = -ENODEV;
		goto out;
	}

	/* Enable PS */
	uint8_t op_mode = 1 << PS_ENABLE_SHIFT;
	ret = i2c_write_byte(i2c_bus, REG_OP_MODE_SEL, op_mode);
	if (ret != 0)
		goto out;

	/* PS Setting: S GAIN: X1, ITIME: 0.4 ms, WTIME: 25 ms */
	uint8_t ps_setting = SET_FIELD_VALUE(PS_GAIN_X1,
					     PS_GAIN_SHIFT,
					     PS_GAIN_MASK) \
			   | SET_FIELD_VALUE(INT_TIME_0_4_MS,
					     INT_TIME_SHIFT,
					     INT_TIME_MASK) \
			   | SET_FIELD_VALUE(WAIT_TIME_25_MS,
					     WAIT_TIME_SHIFT,
					     WAIT_TIME_MASK);
	ret = i2c_write_byte(i2c_bus, REG_PS_SETTING, ps_setting);
	if (ret != 0)
		goto out;

	/* LED pulse: 1 pulse */
	uint8_t pulse_count = 0;
	ret = i2c_write_byte(i2c_bus, REG_LED_PULSE_SETTING, pulse_count);
	if (ret != 0)
		goto out;

	dump_sensor_config(i2c_bus);
out:
	if (i2c_bus > 0 ) close(i2c_bus);
	return ret;
}

int retrieve_sensor_data(uint16_t *ps_val)
{
	int i2c_bus = -1;
	int ret = 0;

	ret = i2c_prepare_bus(&i2c_bus);
	if (ret != 0)
		goto out;

	ret = i2c_read_word(i2c_bus, REG_DATA_LSB, REG_DATA_MSB, ps_val);
out:
	if (i2c_bus > 0 ) close(i2c_bus);
	return ret;
}

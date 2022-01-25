/*
 * Copyright (c) Siemens AG, 2019
 *
 * Authors:
 *  Gao Nian <nian.gao@siemens.com>
 *
 * This file is subject to the terms and conditions of the MIT License.  See
 * COPYING.MIT file in the top-level directory.
 */

#include <linux/serial.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <termios.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <malloc.h>
#include <libusb-1.0/libusb.h>
#include <gpiod.h>
#include <stdarg.h>

typedef unsigned char   BYTE;
typedef unsigned int    UINT;
typedef unsigned short  U16;

typedef enum _E_STATUS {
    e_SUCCESS                 = 0x00,
    e_IO_ERROR                = 0x01,

    e_DEVICE_NOT_FOUND        = 0xFF
} E_STATUS;

#define ERROR(msg, ...)    printf("ERROR: "msg"\n", ##__VA_ARGS__);

typedef enum{
    e_case_sensitive = 0,
    e_case_insensitive
}E_CASE_SENSITIVE;

#define MUTIL_THREAD   100

static char *format(const char *fmt, ...)
{
    #define MAX_STRING_SIZE   128

    static char string[MUTIL_THREAD][MAX_STRING_SIZE] = {{0,0}};

    static int cnt = 0;
    if(cnt == MUTIL_THREAD)
    {
        cnt = 0;
    }

    memset((char *)&string[cnt][0], 0, MAX_STRING_SIZE);

    va_list ap;
    va_start(ap, fmt);
    vsprintf((char *)&string[cnt][0], fmt, ap);
    va_end(ap);

    char *ptr = (char *)&string[cnt][0];
    cnt++;

    return ptr;
}

static char **split(const char *string, const char *delimiter, int *num)
{
    #define MAX_SECTION   20
    static char *args[MUTIL_THREAD][MAX_SECTION] = {{0,0}};

    #define BUF_SIZE   256
    static char buf[MUTIL_THREAD][BUF_SIZE] = {{0,0}};

    static int count = 0;
    if(count == MUTIL_THREAD)
    {
        count = 0;
    }

    memset((char *)&buf[count][0], 0, BUF_SIZE);
    memcpy((char *)&buf[count][0], string, strlen(string));

    int i = 0;
    char *p = strtok((char *)&buf[count][0], delimiter);
    while(NULL != p)
    {
        args[count][i++] = p;
        p = strtok(NULL, delimiter);
    }

    if(NULL != num)
    {
        *num = i;
    }

    char **ptr = &args[count][0];
    count++;

    return ptr;
}

#define ARG(fmt, ...)   split(format(fmt, ##__VA_ARGS__), " ", NULL)

static bool compare_string(const char *dest, const char *arg, const E_CASE_SENSITIVE casesensitive)
{
    const char *DELIMITER = ",";

    int num = 0;
    char **list = split(arg, DELIMITER, &num);

    int i = 0;
    for(i = 0; i < num; i++)
    {
        if(casesensitive == e_case_sensitive)
        {
            if(0 == strncmp(list[i], dest, strlen(dest)))
            {
                return true;
            }
        }
        else
        {
            if(0 == strcasecmp(list[i], dest))
            {
                return true;
            }
        }
    }
    return false;
}

static bool check_arg(int argc, char **argv, const char *name, const E_CASE_SENSITIVE casesensitive)
{
    for(int i = 0; i < argc; i++)
    {
        if(compare_string(argv[i], name, casesensitive))
        {
            return true;
        }
    }

    return false;
}

static int get_arg_int(int argc, char **argv, const char *name, const E_CASE_SENSITIVE casesensitive, int defaultValue)
{
    for(int i = 0; i < argc; i++)
    {
        if(compare_string(argv[i], name, casesensitive)
            && ((i + 1) < argc)
            && ('-' != argv[i + 1][0]))
        {
            return strtol(argv[i + 1], NULL, 0);
        }
    }

    return defaultValue;
}

static char *get_arg_string(int argc, char **argv, const char *name, const E_CASE_SENSITIVE casesensitive, char *defaultValue)
{
    for(int i = 0; i < argc; i++)
    {
        if(compare_string(argv[i], name, casesensitive)
            && ((i + 1) < argc))
        {
            return argv[i + 1];
        }
    }

    return defaultValue;
}


#define   LEN(a)   (sizeof(a)/sizeof((a)[0]))

void gpio_set(const char *line_name, int value)
{
    struct gpiod_line *line;

    line = gpiod_line_find(line_name);
    if (!line) {
        ERROR("Unable to find GPIO line %s", line_name);
        return;
    }

    if (gpiod_line_request_output(line, "switchserialmode", value) < 0) {
        perror("gpiod_line_request_output");
    }

    gpiod_line_release(line);
    gpiod_line_close_chip(line);
}

static void gpio_set_mode(int mode0, int mode1)
{
    gpio_set("UART0-enable", 1);
    gpio_set("UART0-mode0", mode0);
    gpio_set("UART0-mode1", mode1);
}

static void gpio_set_terminate(int onoff)
{
    gpio_set("UART0-terminate", onoff);
}

static void gpio_switch_mode(const char *mode, int terminate)
{
    if(compare_string(mode, "rs232", e_case_insensitive))
    {
        gpio_set_mode(1, 0);
        gpio_set_terminate(0);
    }
    else if(compare_string(mode, "rs485", e_case_insensitive))
    {
        gpio_set_mode(0, 1);
        gpio_set_terminate(terminate);
    }
    else if(compare_string(mode, "rs422", e_case_insensitive))
    {
        gpio_set_mode(1, 1);
        gpio_set_terminate(terminate);
    }
}


#ifndef SER_RS485_TERMINATE_BUS
#define SER_RS485_TERMINATE_BUS     (1 << 5)
#endif

#define SET_UART_RTS_ACTIVE_LOGIC(flags, logic)  \
    do{\
        if(logic){\
            flags &= ~(SER_RS485_RTS_ON_SEND);   \
            flags |= (SER_RS485_RTS_AFTER_SEND); \
        }else{\
            flags |= (SER_RS485_RTS_ON_SEND);     \
            flags &= ~(SER_RS485_RTS_AFTER_SEND);}\
    }while(0)

#define GET_UART_RTS_ACTIVE_LOGIC(flags)  (!((flags) & SER_RS485_RTS_ON_SEND))

static E_STATUS ttyuart_get_rs485conf(const char *uartdev, struct serial_rs485 *pcfg)
{
    int fd = open(uartdev, O_RDWR);
    if(fd < 0)
    {
        ERROR("open %s failed", uartdev);
        return e_IO_ERROR;
    }

    int ret = ioctl(fd, TIOCGRS485, pcfg);
    if(ret < 0)
    {
        perror("Error");
    }

    close(fd);
    return 0 == ret ? e_SUCCESS : e_IO_ERROR;
}

static void ttyuart_print_mode(const char *uartdev)
{
    struct serial_rs485 rs485conf;

    if(e_SUCCESS != ttyuart_get_rs485conf(uartdev, &rs485conf))
    {
        return;
    }

    const char *mode = NULL;
    const char *activelogic = NULL;
    const char *terminate = NULL;

    if(!(rs485conf.flags & SER_RS485_ENABLED))
    {
        mode = "rs232";
        activelogic = "";
        terminate = "";
    }
    else
    {
        if(rs485conf.flags & SER_RS485_RX_DURING_TX)
        {
            mode = "rs422";
            activelogic = "";
        }
        else
        {
            mode = "rs485";
            activelogic = GET_UART_RTS_ACTIVE_LOGIC(rs485conf.flags) ? "active-logic(high)" : "active-logic(low)";
        }

        if(rs485conf.flags & SER_RS485_TERMINATE_BUS)
        {
            terminate = "terminating";
        }
        else
        {
            terminate = "non-terminating";
        }
    }

    printf("%s %s %s\n", mode, activelogic, terminate);
}

static E_STATUS ttyuart_set_rs485conf(const char *uartdev, struct serial_rs485 *pcfg)
{
    int fd = open(uartdev, O_RDWR);
    if(fd < 0)
    {
        ERROR("open %s failed", uartdev);
        return e_IO_ERROR;
    }

    int ret = ioctl(fd, TIOCSRS485, pcfg);
    if(ret < 0)
    {
        perror("Error");
    }

    close(fd);
    return 0 == ret ? e_SUCCESS : e_IO_ERROR;
}

static E_STATUS ttyuart_switchto_rs232(const char *uartdev)
{
    struct serial_rs485 rs485conf;
    memset(&rs485conf, 0, sizeof(rs485conf));

    return ttyuart_set_rs485conf(uartdev, &rs485conf);
}

static E_STATUS ttyuart_switchto_rs485(const char *uartdev, int logicLevel)
{
    struct serial_rs485 rs485conf;
    memset(&rs485conf, 0, sizeof(rs485conf));

    SET_UART_RTS_ACTIVE_LOGIC(rs485conf.flags, logicLevel);

    rs485conf.flags |= SER_RS485_ENABLED;

    return ttyuart_set_rs485conf(uartdev, &rs485conf);
}

static E_STATUS ttyuart_switchto_rs422(const char *uartdev, int logicLevel)
{
    struct serial_rs485 rs485conf;
    memset(&rs485conf, 0, sizeof(rs485conf));

    SET_UART_RTS_ACTIVE_LOGIC(rs485conf.flags, logicLevel);

    rs485conf.flags |= SER_RS485_ENABLED | SER_RS485_RX_DURING_TX;

    return ttyuart_set_rs485conf(uartdev, &rs485conf);
}

const char * const TTYUART_USAGE = "\
It's to operate tty serial device.\n\
    -h,--help: display help information.\n\
    -D,--device: specified device, like '/dev/ttyS1' etc.\n\
    -m,--mode mode: set serial work mode, the mode can be set 'rs232' or 'rs485' or 'rs422'.\n\
    -l,--logic level: set RTS-pin logic level when sending in rs485 mode, logic can be set '0' or '1'.\n\
    -d,--display: display the current mode of ttyuart\n";

static void ttyuart_command_handle(int argc, char **argv)
{
    if(check_arg(argc, argv, "-h,--help", e_case_sensitive))
    {
        printf("%s", TTYUART_USAGE);
        return;
    }

    const char *devType = get_arg_string(argc, argv, "-D,--device", e_case_sensitive, NULL);
    if(NULL == devType)
    {
        ERROR("parameter error, must specify serial device via '-D,--device'");
        return;
    }

    if(check_arg(argc, argv, "-d,--display", e_case_sensitive))
    {
        ttyuart_print_mode(devType);
        return;
    }

    const char *mode = get_arg_string(argc, argv, "-m,--mode", e_case_sensitive, NULL);
    if(NULL == mode)
    {
        ERROR("parameter error, must specify mode via '-m,--mode'");
        return;
    }

    int logicLevel = get_arg_int(argc, argv, "-l,--logic", e_case_sensitive, 1);

    if(0 == strcasecmp(mode, "rs232"))
    {
        ttyuart_switchto_rs232(devType);
    }
    else if(0 == strcasecmp(mode, "rs485"))
    {
        ttyuart_switchto_rs485(devType, logicLevel);
    }
    else if(0 == strcasecmp(mode, "rs422"))
    {
        ttyuart_switchto_rs422(devType, logicLevel);
    }
    else
    {
        ERROR("parameter error, don't support '%s'", mode);
    }
}



/* Device Part Numbers */
typedef enum _SILABS_PARTNUM_CPXXXX {
    CP210x_PARTNUM_UNKNOWN =  ((BYTE)(0xFF & 0x00)),
    CP210x_PARTNUM_CP2101 = ((BYTE)(0xFF & 0x01)),
    CP210x_PARTNUM_CP2102 = ((BYTE)(0xFF & 0x02)),
    CP210x_PARTNUM_CP2103 = ((BYTE)(0xFF & 0x03)),
    CP210x_PARTNUM_CP2104 = ((BYTE)(0xFF & 0x04)),
    CP210x_PARTNUM_CP2105 = ((BYTE)(0xFF & 0x05)),
    CP210x_PARTNUM_CP2108 = ((BYTE)(0xFF & 0x08)),
    CP210x_PARTNUM_CP2109 = ((BYTE)(0xFF & 0x09)),

    SILABS_PARTNUM_CP2110 = ((BYTE)(0xFF & 0x0A)),
    HID_UART_PART_CP2110 = SILABS_PARTNUM_CP2110,

    CP210x_PARTNUM_CP2112 = ((BYTE)(0xFF & 0x0C)),
    HID_SMBUS_PART_CP2112 = CP210x_PARTNUM_CP2112,

    SILABS_PARTNUM_CP2114 = ((BYTE)(0xFF & 0x0E)),
    HID_UART_PART_CP2114 = SILABS_PARTNUM_CP2114,

    CP210x_PARTNUM_CP2102N_QFN28 = ((BYTE)(0xFF & 0x20)),
    CP210x_PARTNUM_CP2102N_QFN24 = ((BYTE)(0xFF & 0x21)),
    CP210x_PARTNUM_CP2102N_QFN20 = ((BYTE)(0xFF & 0x22)),

    CP210x_PARTNUM_USBXPRESS_F3XX = ((BYTE)(0xFF & 0x80)),
    CP210x_PARTNUM_USBXPRESS_EFM8 = ((BYTE)(0xFF & 0x80)),
    CP210x_PARTNUM_USBXPRESS_EFM32 = ((BYTE)(0xFF & 0x81))
}SILABS_PARTNUM_CPXXXX;

struct cp210x_info{
    SILABS_PARTNUM_CPXXXX partnum;
    const char * const name;
};

const struct cp210x_info cp210x_info_list[] = {
    {CP210x_PARTNUM_CP2101, "CP2101"},
    {CP210x_PARTNUM_CP2102, "CP2102"},
    {CP210x_PARTNUM_CP2103, "CP2103"},
    {CP210x_PARTNUM_CP2104, "CP2104"},
    {CP210x_PARTNUM_CP2105, "CP2105"},
    {CP210x_PARTNUM_CP2108, "CP2108"},
    {CP210x_PARTNUM_CP2109, "CP2109"},

    {SILABS_PARTNUM_CP2110, "CP2110"},
    {CP210x_PARTNUM_CP2112, "CP2112"},
    {SILABS_PARTNUM_CP2114, "CP2114"},

    {CP210x_PARTNUM_CP2102N_QFN28, "CP2102N28"},
    {CP210x_PARTNUM_CP2102N_QFN24, "CP2102N24"},
    {CP210x_PARTNUM_CP2102N_QFN20, "CP2102N20"}};

static libusb_context *g_LibusbContext = NULL;

static const char *cp210x_find_name(SILABS_PARTNUM_CPXXXX partnum)
{
    for(int i = 0; i < sizeof(cp210x_info_list)/sizeof(cp210x_info_list[0]); i++)
    {
        if(cp210x_info_list[i].partnum == partnum)
        {
            return cp210x_info_list[i].name;
        }
    }

    return NULL;
}

static SILABS_PARTNUM_CPXXXX cp210x_find_partnum(const char *name)
{
    for(int i = 0; i < sizeof(cp210x_info_list)/sizeof(cp210x_info_list[0]); i++)
    {
        if(0 == strcasecmp(cp210x_info_list[i].name, name))
        {
            return cp210x_info_list[i].partnum;
        }
    }

    return CP210x_PARTNUM_UNKNOWN;
}

static bool is_valid_cp210x_partnum(const SILABS_PARTNUM_CPXXXX _v)
{
    return (((CP210x_PARTNUM_CP2101 <= _v) && (_v <= CP210x_PARTNUM_CP2105))
                || (CP210x_PARTNUM_CP2108 == _v)
                || (CP210x_PARTNUM_CP2109 == _v)
                || (CP210x_PARTNUM_CP2112 == _v)
                || ((CP210x_PARTNUM_CP2102N_QFN28 <= _v) && (_v <= CP210x_PARTNUM_CP2102N_QFN20))
                || (CP210x_PARTNUM_USBXPRESS_F3XX == _v));
}

static bool cp210x_is_candidate_device(libusb_device *pdev)
{
    bool isCandidateDevice = false;   /* innocent til proven guilty */
    struct libusb_device_descriptor devDesc;

    if(0 != libusb_get_device_descriptor(pdev, &devDesc))
    {
        return isCandidateDevice;
    }

    switch(devDesc.bDeviceClass)
    {
        case LIBUSB_CLASS_PER_INTERFACE:  /* CP2102, CP2112,  */
            if((1 == devDesc.iManufacturer) && (2 == devDesc.iProduct) && (3 <= devDesc.iSerialNumber))
            {
                struct libusb_config_descriptor *pconfigDesc = NULL;
                isCandidateDevice = true;

                if(0 == libusb_get_config_descriptor(pdev, 0, &pconfigDesc))
                {
                    if(pconfigDesc->bNumInterfaces
                        && pconfigDesc->interface->num_altsetting
                        && (LIBUSB_CLASS_VENDOR_SPEC != pconfigDesc->interface->altsetting->bInterfaceClass))
                    {
                        isCandidateDevice = false;
                    }

                    libusb_free_config_descriptor(pconfigDesc);
                    pconfigDesc = (struct libusb_config_descriptor *)NULL;
               }
            }
            break;

        default:
            isCandidateDevice = false;
            break;
    }

    return isCandidateDevice;
}

static E_STATUS cp210x_get_partnumber(libusb_device_handle *h, BYTE *partnum)
{
    int ret = libusb_control_transfer(h, 0xC0, 0xFF, 0x370B, 0x0000, partnum, 1, 7000);

    if(1 == ret)
    {
        return e_SUCCESS;
    }

    if(LIBUSB_ERROR_TIMEOUT == ret)
    {
        ERROR("libusb_control_transfer timeout");
        return e_IO_ERROR;
    }

    struct libusb_config_descriptor *configDesc = NULL;
    E_STATUS status = e_IO_ERROR;

    if(0 == libusb_get_config_descriptor(libusb_get_device(h), 0, &configDesc))
    {
        /* Looking for a very particular fingerprint to conclude the device is a CP2101 */
        if ((configDesc->bNumInterfaces > 0)
            && (configDesc->interface[0].altsetting->bNumEndpoints > 1)
            && ((configDesc->interface[0].altsetting->endpoint[0].bEndpointAddress & 0x0F) == 0x03)
            && ((configDesc->interface[0].altsetting->endpoint[1].bEndpointAddress & 0x0F) == 0x03))
        {
            *partnum = CP210x_PARTNUM_CP2101;
            status = e_SUCCESS;
        }

        libusb_free_config_descriptor(configDesc);
    }

    return status;
}

static E_STATUS cp210x_read_config(libusb_device_handle *usbhd, BYTE *config, UINT len)
{
    UINT rlen = libusb_control_transfer(usbhd, 0xC0, 0xFF,
                                                     0x0E, /* wValue */
                                                        0, /* WIndex */
                                                   config, /* data */
                                                      len, /* data size */
                                                        0);

    return (rlen == len) ? e_SUCCESS : e_IO_ERROR;
}

static E_STATUS cp210x_write_config(libusb_device_handle *usbhd, BYTE *config, UINT len)
{
    UINT wlen = libusb_control_transfer(usbhd, 0x40, 0xFF,
                                                   0x370F, /* wValue */
                                                        0, /* WIndex */
                                                   config, /* data */
                                                      len, /* data size */
                                                        0);

    return (wlen == len) ? e_SUCCESS : e_IO_ERROR;
}

static int cp210x_list(const char **namelist, int len)
{
    libusb_device_handle *usbh = NULL;
    libusb_device **list = NULL;

    /* Enumerate all USB devices, returning the number of USB devices and a list of those devices */
    const ssize_t numOfUSBDevices = libusb_get_device_list(g_LibusbContext, &list);

    /* A negative count indicates an error */
    if(numOfUSBDevices < 0)
    {
        ERROR("libusb_get_device_list error");
        return 0;
    }

    int n = 0;

    for(ssize_t i = 0; i < numOfUSBDevices; i++)
    {
        libusb_device *device = list[i];
        libusb_device_handle *h = NULL;

        if(cp210x_is_candidate_device(device) && (0 == libusb_open(list[i], &h)))
        {
            BYTE partNum = 0;

            if((0 == cp210x_get_partnumber(h, &partNum))
                && is_valid_cp210x_partnum((SILABS_PARTNUM_CPXXXX)partNum))
            {
                if(n < len)
                {
                    namelist[n++] = cp210x_find_name(partNum);
                }
            }

            libusb_close(h);
        }
    } /* end for */

    libusb_free_device_list(list, 1); /* Unreference all devices to free the device list */
    return n;
}

static libusb_device_handle *cp210x_open(SILABS_PARTNUM_CPXXXX cp210x_partnum)
{
    libusb_device_handle *usbh = NULL;
    libusb_device **list = NULL;

    /* Enumerate all USB devices, returning the number of USB devices and a list of those devices */
    const ssize_t numOfUSBDevices = libusb_get_device_list(g_LibusbContext, &list);

    /* A negative count indicates an error */
    if(numOfUSBDevices < 0)
    {
        ERROR("libusb_get_device_list error");
        return NULL;
    }

    for(ssize_t i = 0; i < numOfUSBDevices; i++)
    {
        libusb_device *device = list[i];
        libusb_device_handle *h = NULL;

        if(cp210x_is_candidate_device(device) && (0 == libusb_open(list[i], &h)))
        {
            BYTE partNum = 0;

            if((0 == cp210x_get_partnumber(h, &partNum))
                && is_valid_cp210x_partnum((SILABS_PARTNUM_CPXXXX)partNum)
                && (partNum == cp210x_partnum))
            {
                if(NULL == usbh)
                {
                    usbh = h;
                }
                else
                {
                    ERROR("conflicts, find multi '%s'", cp210x_find_name(partNum));
                    libusb_close(usbh);
                    libusb_close(h);
                    return NULL;
                }
            }
            else
            {
                libusb_close(h);
            }
        }
    } /* end for */

    libusb_free_device_list(list, 1);
    return usbh;
}

static void cp210x_close(libusb_device_handle *usbh)
{
    if(NULL != usbh)
    {
        libusb_close(usbh);
    }
}

static void cp210x_reset(libusb_device_handle *usbh)
{
    if(NULL != usbh)
    {
        libusb_reset_device(usbh);
    }
}

static U16 fletcher16(const BYTE *bytes, U16 len)
{
    U16 sum1 = 0xff, sum2 = 0xff;
    U16 tlen = 0;

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

static void cp210x_compute_configure_checksum(BYTE *config, U16 len)
{
    U16 checksum = fletcher16(config, len - 2);
    config[len - 2] = (BYTE)((checksum >> 8) & 0xff);
    config[len - 1] = (BYTE)((checksum) & 0xff);
}

#define MAIN_GPIO_CONTROL_1_INDEX      600
#define CP2102N_RS485_BIT              4
#define MAIN_GPIO_CONTROL_2_INDEX      601
#define CP2102N_RS485_LOGIC_BIT        0
#define CP2102N_RS485_SETUP_INDEX      669
#define CP2102N_RS485_HOLD_INDEX       671
#define MAIN_RESET_LATCH_P1_INDEX      587
#define CP2102N_GPIO2_RESET_LATH_BIT   5

#define SET_CP2102N_RS485PIN_TO_RS585(config)   ((config)[MAIN_GPIO_CONTROL_1_INDEX] |= (BYTE)(1 << CP2102N_RS485_BIT))
#define IS_CP2102N_RS485PIN_RS485_MODE(config)    ((config)[MAIN_GPIO_CONTROL_1_INDEX] & (1 << CP2102N_RS485_BIT))
#define SET_CP2102N_RS485PIN_TO_GPIO(config)    ((config)[MAIN_GPIO_CONTROL_1_INDEX] &= (BYTE)(~(1 << CP2102N_RS485_BIT)))

#define SET_CP2102N_RS485PIN_RS485_ACTIVE_LOGIC(config, logic)\
    do{\
        if(logic)\
            config[MAIN_GPIO_CONTROL_2_INDEX] |= (BYTE)(1 << CP2102N_RS485_LOGIC_BIT);   \
        else \
            config[MAIN_GPIO_CONTROL_2_INDEX] &= (BYTE)(~(1 << CP2102N_RS485_LOGIC_BIT));\
    }while(0)

#define IS_CP2102N_RS485PIN_RS485_LOGIC(config)   (config[MAIN_GPIO_CONTROL_2_INDEX] & (1 << CP2102N_RS485_LOGIC_BIT))

#define SET_CP2102N_GPIO2_RESET_LATH(config, logic) \
    do{\
        if(logic)\
            config[MAIN_RESET_LATCH_P1_INDEX] |= (BYTE)(1 << CP2102N_GPIO2_RESET_LATH_BIT);   \
        else\
            config[MAIN_RESET_LATCH_P1_INDEX] &= (BYTE)(~(1 << CP2102N_GPIO2_RESET_LATH_BIT));   \
    }while(0)

#define GET_CP2102N_GPIO2_RESET_LATH(config)   (config[MAIN_RESET_LATCH_P1_INDEX] & (BYTE)(1 << CP2102N_GPIO2_RESET_LATH_BIT))

#define SET_CP2102N_RS485_SETUP_TIME(config, u16vl) \
    do{\
        config[CP2102N_RS485_SETUP_INDEX] = (BYTE)(((u16vl) >> 8) & 0xff); \
        config[CP2102N_RS485_SETUP_INDEX + 1] = (BYTE)((u16vl) & 0xff);    \
    }while(0)

#define GET_CP2102N_RS485_SETUP_TIME(config)   (((config[CP2102N_RS485_SETUP_INDEX] << 8) & 0xff00) | (config[CP2102N_RS485_SETUP_INDEX + 1] & 0xff))

#define CFG_CP2102N_RS485_HOLD_TIME(config, u16vl) \
    do{\
        config[CP2102N_RS485_HOLD_INDEX] = (BYTE)(((u16vl) >> 8) & 0xff); \
        config[CP2102N_RS485_HOLD_INDEX + 1] = (BYTE)((u16vl) & 0xff);    \
    }while(0)

#define GET_CP2102N_RS485_HOLD_TIME(config)   (((config[CP2102N_RS485_HOLD_INDEX] << 8) & 0xff00) | (config[CP2102N_RS485_HOLD_INDEX + 1] & 0xff))


const char * const CP210X_USAGE = "\
It's to operate cp210x device.\n\
    -h,--help: display help information.\n\
    -l,--list: list cp210x device.\n\
    -D,--device: specified device, like 'cp2102', 'cp2102n24', 'cp2102n28' etc.\n\
    -r,--read-config filename: read configuration from cp210x to filename.\n\
    -w,--write-config filename: write configuration from filename to cp210x.\n\
    -m,--rs485pin mode: set rs485-pin work mode, the mode can be set 'gpio' or 'rs485'.\n\
    -g,--rs485-logic logic: set rs485-pin logic level when sending in rs485 mode, logic can be set '0' or '1'.\n\
    -s,--setup u16: set rs485-pin's setup time in rs485 mode.\n\
    -o,--hold u16: set rs485-pin's hold time in rs485 mode.\n\
    -d,--display: display the current mode of cp210x.\n\
    -v,--reset-level: set rs485-pin's default logic level in gpio mode.\n\
    -e,--reset: reset cp210x.\n";


typedef enum {
    e_CONTINUE = 0,
    e_STOP,
}E_CMD_EXE_STATUS;

#define CP210x_MAX_CONFIG_LENGTH  0x02a6

typedef E_CMD_EXE_STATUS (*cmd_hander)(int argc, char **argv);

static U16 g_CheckSumOld = 0;

static libusb_device_handle *cp210x_cmd_open_device(int argc, char **argv)
{
    static libusb_device_handle *usbhd = NULL;
    if(NULL != usbhd)
    {
        return usbhd;
    }

    SILABS_PARTNUM_CPXXXX ePartNum = CP210x_PARTNUM_UNKNOWN;
    const char *devType = get_arg_string(argc, argv, "-D,--device", e_case_sensitive, NULL);
    if(devType)
    {
        ePartNum = cp210x_find_partnum(devType);
        if(CP210x_PARTNUM_UNKNOWN == ePartNum)
        {
            ERROR("parameter error, don't support '%s'", devType);
            return NULL;
        }
    }
    else
    {
        ERROR("parameter error, must specify cp210x device via '-D,--device'");
        return NULL;
    }

    usbhd = cp210x_open(ePartNum);
    if(NULL == usbhd)
    {
        ERROR("open '%s' failed", devType);
    }

    return usbhd;
}

static BYTE *cp210x_cmd_get_config(int argc, char **argv)
{
    static BYTE config[CP210x_MAX_CONFIG_LENGTH] = {0};

    static bool isGeted = false;
    if(isGeted)
    {
        return config;
    }

    libusb_device_handle *usbhd = cp210x_cmd_open_device(argc, argv);
    if(NULL == usbhd)
    {
        return NULL;
    }

    memset((char*)(&(config[0])), 0, CP210x_MAX_CONFIG_LENGTH);

    if(e_SUCCESS != cp210x_read_config(usbhd, config, CP210x_MAX_CONFIG_LENGTH))
    {
        ERROR("cp210x_read_config failed");
        return NULL;
    }

    g_CheckSumOld = ((config[CP210x_MAX_CONFIG_LENGTH - 2] << 8) & 0xff00) | (config[CP210x_MAX_CONFIG_LENGTH - 1] & 0xff);
    isGeted = true;

    return config;
}

static E_CMD_EXE_STATUS cp210x_cmd_help(int argc, char **argv)
{
    printf("%s", CP210X_USAGE);
    return e_STOP;;
}

static E_CMD_EXE_STATUS cp210x_cmd_list(int argc, char **argv)
{
    #define MAX_NUM   10
    const char *namelist[MAX_NUM] = {0};
    int num = cp210x_list(namelist, MAX_NUM);

    int i = 0;
    for(i = 0; i < num; i++)
    {
        if(0 == i)
        {
            printf("Find cp210x:\n");
        }
        printf("\t%s\n", namelist[i]);
    }

    return e_STOP;
}

static E_CMD_EXE_STATUS cp210x_cmd_print_mode(int argc, char **argv)
{
    BYTE *config = cp210x_cmd_get_config(argc, argv);
    if(NULL == config)
    {
        return e_STOP;
    }

    if(IS_CP2102N_RS485PIN_RS485_MODE(config))
    {
        printf("rs485 active-logic(%s) setup-time(0x%04x) hold-time(0x%04x)\n"
                        , IS_CP2102N_RS485PIN_RS485_LOGIC(config) ? "high" : "low"
                        , GET_CP2102N_RS485_SETUP_TIME(config)
                        , GET_CP2102N_RS485_HOLD_TIME(config));
    }
    else
    {
        printf("gpio reset-logic(%s)\n", GET_CP2102N_GPIO2_RESET_LATH(config) ? "high" : "low");
    }

    return e_STOP;
}

static E_CMD_EXE_STATUS cp210x_cmd_read_config(int argc, char **argv)
{
    const char *saveName = get_arg_string(argc, argv, "-r,--read-config", e_case_sensitive, NULL);
    if(NULL == saveName)
    {
        ERROR("parameter error, '-r,--read-config' must append a file name");
        return e_STOP;
    }

    BYTE *config = cp210x_cmd_get_config(argc, argv);
    if(NULL == config)
    {
        return e_STOP;
    }

    FILE *fp = fopen(saveName, "w");

    #define TMP_SIZE 10
    char tmp[TMP_SIZE] = {0};
    int i = 0;
    for(i = 0; i < CP210x_MAX_CONFIG_LENGTH; i++)
    {
        memset(tmp, TMP_SIZE, 0);
        sprintf(tmp, "0x%02x\n", config[i]);
        fwrite(tmp, 1, strlen(tmp), fp);
    }

    fclose(fp);
    return e_CONTINUE;
}

static E_CMD_EXE_STATUS cp210x_cmd_write_config(int argc, char **argv)
{
    const char *configName = get_arg_string(argc, argv, "-w,--write-config", e_case_sensitive, NULL);
    if(NULL == configName)
    {
        ERROR("parameter error, '-w,--write-config' must append a file name");
        return e_STOP;
    }

    BYTE config[CP210x_MAX_CONFIG_LENGTH] = {0};

    FILE *fp = fopen(configName, "r");
    if(NULL == fp)
    {
        ERROR("open '%s' failed", configName);
        return e_STOP;
    }

    #define MAX_LINE   10
    char tmp[MAX_LINE] = {0};
    int i = 0;

    while(!feof(fp) && (i < CP210x_MAX_CONFIG_LENGTH))
    {
        memset(tmp, 0, MAX_LINE);
        fgets(tmp, MAX_LINE, fp);
        config[i++] = strtol(tmp, NULL, 0);
    }

    fclose(fp);

    libusb_device_handle *usbhd = cp210x_cmd_open_device(argc, argv);
    if(NULL == usbhd)
    {
        return e_STOP;
    }

    cp210x_compute_configure_checksum(config, CP210x_MAX_CONFIG_LENGTH);

    if(e_SUCCESS != cp210x_write_config(usbhd, config, CP210x_MAX_CONFIG_LENGTH))
    {
        ERROR("cp210x_write_config failed");
        return e_STOP;
    }

    return e_CONTINUE;
}

static E_CMD_EXE_STATUS cp210x_cmd_set_mode(int argc, char **argv)
{
    const char *mode = get_arg_string(argc, argv, "-m,--rs485pin", e_case_sensitive, NULL);
    if(NULL == mode)
    {
        ERROR("parameter error, '-m,--rs485pin' must append a mode");
        return e_STOP;
    }

    BYTE *config = cp210x_cmd_get_config(argc, argv);
    if(NULL == config)
    {
        return e_STOP;
    }

    if(0 == strcasecmp(mode, "gpio"))
    {
        SET_CP2102N_RS485PIN_TO_GPIO(config);

    }
    else if(0 == strcasecmp(mode, "rs485"))
    {
        SET_CP2102N_RS485PIN_TO_RS585(config);
    }
    else
    {
        ERROR("parameter error, '-m,--rs485pin' must append a mode, it can be 'gpio' or 'rs485'");
        return e_STOP;
    }

    return e_CONTINUE;
}

static E_CMD_EXE_STATUS cp210x_cmd_set_rs485_logic(int argc, char **argv)
{
    const int logic = get_arg_int(argc, argv, "-g,--rs485-logic", e_case_sensitive, -1);
    if(-1 == logic)
    {
        ERROR("parameter error, '-g,--rs485-logic' must append a value, like '0' or '1'");
        return e_STOP;
    }

    BYTE *config = cp210x_cmd_get_config(argc, argv);
    if(NULL == config)
    {
        return e_STOP;
    }

    SET_CP2102N_RS485PIN_RS485_ACTIVE_LOGIC(config, logic);

    return e_CONTINUE;
}

static E_CMD_EXE_STATUS cp210x_cmd_set_rs485_setup(int argc, char **argv)
{
    const int setuptime = get_arg_int(argc, argv, "-s,--setup", e_case_sensitive, -1);
    if(-1 == setuptime)
    {
        ERROR("parameter error, '-s,--setup' must append a unsigned short type value, like '0x1234' or '1234'");
        return e_STOP;
    }

    BYTE *config = cp210x_cmd_get_config(argc, argv);
    if(NULL == config)
    {
        return e_STOP;
    }

    SET_CP2102N_RS485_SETUP_TIME(config, setuptime);
    return e_CONTINUE;
}

static E_CMD_EXE_STATUS cp210x_cmd_set_rs485_hold(int argc, char **argv)
{
    const int holdtime = get_arg_int(argc, argv, "-o,--hold", e_case_sensitive, -1);
    if(-1 == holdtime)
    {
        ERROR("parameter error, '-o,--hold' must append a unsigned short type value, like '0x1234' or '1234'");
        return e_STOP;
    }

    BYTE *config = cp210x_cmd_get_config(argc, argv);
    if(NULL == config)
    {
        return e_STOP;
    }

    CFG_CP2102N_RS485_HOLD_TIME(config, holdtime);
    return e_CONTINUE;
}

static E_CMD_EXE_STATUS cp210x_cmd_set_rs485pin_gpio_reset_level(int argc, char **argv)
{
    int rstLogic = get_arg_int(argc, argv, "-v,--reset-level", e_case_sensitive, -1);
    if(-1 == rstLogic)
    {
        ERROR("parameter error, '-o,--hold' must append a value, like '0' or '1'");
        return e_STOP;
    }

    BYTE *config = cp210x_cmd_get_config(argc, argv);
    if(NULL == config)
    {
        return e_STOP;
    }

    SET_CP2102N_GPIO2_RESET_LATH(config, rstLogic);
    return e_CONTINUE;
}

static E_CMD_EXE_STATUS cp210x_cmd_reset(int argc, char **argv)
{
    cp210x_reset(cp210x_cmd_open_device(argc, argv));
    return e_STOP;
}

typedef struct {
    const char *const cmd;
    cmd_hander cmd_func;
}cmd_list_t;

cmd_list_t cmd_list[] = {
    {"-h,--help",    cp210x_cmd_help},
    {"-l,--list",    cp210x_cmd_list},
    {"-d,--display", cp210x_cmd_print_mode},
    {"-r,--read-config", cp210x_cmd_read_config},
    {"-w,--write-config", cp210x_cmd_write_config},
    {"-m,--rs485pin", cp210x_cmd_set_mode},
    {"-g,--rs485-logic", cp210x_cmd_set_rs485_logic},
    {"-s,--setup", cp210x_cmd_set_rs485_setup},
    {"-o,--hold", cp210x_cmd_set_rs485_hold},
    {"-v,--reset-level", cp210x_cmd_set_rs485pin_gpio_reset_level},
    {"-e,--reset", cp210x_cmd_reset}};

static void cp210x_command_handle(int argc, char **argv)
{
    libusb_init(&g_LibusbContext);

    const int size = sizeof(cmd_list) / sizeof(cmd_list[0]);
    int i = 0;
    for(i = 0; i < size; i++)
    {
        if(check_arg(argc, argv, cmd_list[i].cmd, e_case_sensitive))
        {
            if(e_STOP == cmd_list[i].cmd_func(argc, argv))
            {
                break;
            }
        }
    }

    if(g_CheckSumOld)
    {
        libusb_device_handle *usbhd = cp210x_cmd_open_device(argc, argv);

        BYTE *config = cp210x_cmd_get_config(argc, argv);
        if(NULL != config)
        {
            cp210x_compute_configure_checksum(config, CP210x_MAX_CONFIG_LENGTH);
            const U16 checkSumNew = ((config[CP210x_MAX_CONFIG_LENGTH - 2] << 8) & 0xff00) | (config[CP210x_MAX_CONFIG_LENGTH - 1] & 0xff);

            if(g_CheckSumOld != checkSumNew)
            {
                if(e_SUCCESS != cp210x_write_config(usbhd, config, CP210x_MAX_CONFIG_LENGTH))
                {
                    ERROR("cp210x_write_config failed");
                }
            }
        }

        cp210x_close(usbhd);
    }

    libusb_exit(g_LibusbContext);
}

static void cp210x_hardware_reset(void)
{
    usleep(60*1000);
    gpio_set("CP2102N-RESET", 0);
    sleep(1);
    gpio_set("CP2102N-RESET", 1);
}

static void print_usage(const char *name)
{
    printf("\
It's used to set external serial port mode.\n\
Usage:\n\
    %s [ttyuart [options]] | [cp210x [options]] | [-m,--mode MODE]\n\n\
Example:\n\
    %s ttyuart -h\n\
    %s cp210x -h\n\
    %s -m,--mode <rs232 | rs485 | rs422> [-t,--terminate]\n\
        -t,--terminate: Terminate the rs422 or rs485 bus.\n"
           , name, name, name, name);
}

int main(int argc, char **argv)
{
    if(1 == argc)
    {
        ERROR("parameter error\n");
        print_usage(argv[0]);
    }
    else if(compare_string(argv[1], "-h,--help", e_case_insensitive))
    {
        print_usage(argv[0]);
    }
    else if(compare_string(argv[1], "ttyuart", e_case_insensitive))
    {
        ttyuart_command_handle(argc, argv);
    }
    else if(compare_string(argv[1], "cp210x", e_case_insensitive))
    {
        cp210x_command_handle(argc, argv);
    }
    else if(compare_string(argv[1], "-m,--mode", e_case_insensitive))
    {
        const int terminate = check_arg(argc, argv, "-t,--terminate", e_case_sensitive);
        const char *mode = get_arg_string(argc, argv, "-m", e_case_sensitive, NULL);
        if(NULL != mode)
        {
            gpio_switch_mode(mode, terminate);
        }
    }
     else if(compare_string(argv[1], "-r,--reset", e_case_insensitive))
    {
        cp210x_hardware_reset();
    }
    else
    {
        ERROR("parameter error\n");
        print_usage(argv[0]);
    }

    return 0;
}

#ifndef SWITCH_SERIAL_MODE
#define SWITCH_SERIAL_MODE

#include <stdint.h>

#define ERROR       -1
#define SUCCESS     0

typedef enum boardType {
    BASIC_BOARD = 0,
    ADVANCED_BOARD,
    ADVANCED_BOARD_PG1
} boardType_e;

typedef struct transceiver_ops {
    void (*transceiver_set_termination)( uint8_t onoff);
    void (*transceiver_switch_mode)(const uint8_t *mode);
} transceiver_ops_t;

typedef struct serial_ops {
    /*Device node*/
    uint8_t *devName;

    /*Init device resources*/
    int8_t (*init)(uint8_t *devName);

    /*Set serial mode,like rs232 rs485 rs422*/
    void (*setMode)(uint8_t *mode);

    /*Display current serial mode*/
    void (*getMode)(void);

    /*For the device which support setup and hold time*/
    void (*rs485HoldTime)(uint8_t time);
    void (*rs485SetupTime)(uint8_t time);

    /*Release*/
    void (*release)(void);

    void (*preProcess)(void *);
} serial_ops_t;

typedef struct controller_setting {
    uint32_t hold_time;
    uint32_t setup_time;
} controller_setting_t;

typedef struct platform {
    serial_ops_t *serOps;
    transceiver_ops_t *transOps;
    void *private_data;
} platform_t;

boardType_e get_board_type(void);

#endif

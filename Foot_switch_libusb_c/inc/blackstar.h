#include <stdio.h> 
#include <wchar.h> 
#include <inttypes.h>
#include <string.h>
#include <pthread.h>

#include "hidapi.h"

#define MAX_STR         255
#define HID_PACK_SIZE   64
#define VENDOR_ID       0x27d4
#define PRODUCT_ID      0x0012

#define BLACKSTAR_INSTANCE          &(g_blackstar)

#define DO_NOTHING
#define ASSERT_IF_FALSE(con)        RET_ERR_IF_FALSE(con, BLACKSTAR_ERROR_ASSERT)
#define ERR_IF_NOT_CONN             RET_ERR_IF_FALSE(BLACKSTAR_INSTANCE.is_connected, BLACKSTAR_ERROR_NOT_CONNECTED)
#define RET_ERR_IF_FALSE(con, err)  {   \
    if(con)                             \
    {                                   \
        DO_NOTHING;                     \
    }                                   \
    else                                \
    {                                   \
        return err;                     \
    }                                   \
}

typedef enum blackstar_err
{
    BLACKSTAR_SUCCESS,
    BLACKSTAR_ERROR,
    BLACKSTAR_ERROR_ASSERT,
    BLACKSTAR_ERROR_IO,
    BLACKSTAR_ERROR_NOT_CONNECTED,
    BLACKSTAR_ERROR_NOT_SUPPORTED
}blackstar_err_t;

typedef enum blackstar_cmd
{
    BLACKSTAR_CMD_CTRL                       = 0x03
} blackstar_cmd_t;

typedef enum blackstar_ctrl_name
{
    BLACKSTAR_CTRL_NAME_VOICE                = 0x01,
    BLACKSTAR_CTRL_NAME_GAIN                 = 0x02,
    BLACKSTAR_CTRL_NAME_VOLUME               = 0x03,
    BLACKSTAR_CTRL_NAME_BASS                 = 0x04,
    BLACKSTAR_CTRL_NAME_MIDDLE               = 0x05,
    BLACKSTAR_CTRL_NAME_TREBLE               = 0x06,
    BLACKSTAR_CTRL_NAME_ISF                  = 0x07,
    BLACKSTAR_CTRL_NAME_TVP_VALVE            = 0x08,
    BLACKSTAR_CTRL_NAME_RESONANCE            = 0x0B,
    BLACKSTAR_CTRL_NAME_PRESENCE             = 0x0C,
    BLACKSTAR_CTRL_NAME_MASTER_VOLUME        = 0x0D,
    BLACKSTAR_CTRL_NAME_TVP_SWITCH           = 0x0E,
    BLACKSTAR_CTRL_NAME_MOD_SWITCH           = 0x0F,
    BLACKSTAR_CTRL_NAME_DELAY_SWITCH         = 0x10,
    BLACKSTAR_CTRL_NAME_REVERB_SWITCH        = 0x11,
    BLACKSTAR_CTRL_NAME_MOD_TYPE             = 0x12,
    BLACKSTAR_CTRL_NAME_MOD_SEGVAL           = 0x13,
    BLACKSTAR_CTRL_NAME_MOD_MANUAL           = 0x14, 
    BLACKSTAR_CTRL_NAME_MOD_LEVEL            = 0x15,
    BLACKSTAR_CTRL_NAME_MOD_SPEED            = 0x16,
    BLACKSTAR_CTRL_NAME_DELAY_TYPE           = 0x17,
    BLACKSTAR_CTRL_NAME_DELAY_FEEDBACK       = 0x18,   
    BLACKSTAR_CTRL_NAME_DELAY_LEVEL          = 0x1A,
    BLACKSTAR_CTRL_NAME_DELAY_TIME           = 0x1B,
    BLACKSTAR_CTRL_NAME_DELAY_TIME_COARSE    = 0x1C,
    BLACKSTAR_CTRL_NAME_REVERB_TYPE          = 0x1D,
    BLACKSTAR_CTRL_NAME_REVERB_SIZE          = 0x1E,  
    BLACKSTAR_CTRL_NAME_REVERB_LEVEL         = 0x20,
    BLACKSTAR_CTRL_NAME_FX_FOCUS             = 0x24,
} blackstar_ctrl_name_t;

typedef struct blackstar_ctrl
{
    blackstar_ctrl_name_t ctrl_name;
    uint8_t ctrl_range_dev;
    double ctrl_range_human;
    uint8_t ctrl_curr_val;
}blackstar_ctrl_t;

typedef struct blackstar
{
    hid_device * device;
    uint8_t is_connected;
    blackstar_ctrl_t * blackstar_ctrl;
    wchar_t man_str [MAX_STR];
    wchar_t prod_str[MAX_STR];
    uint8_t u8_push_pull[ HID_PACK_SIZE ];
} blackstar_t;

typedef struct pthread_shared
{
    uint8_t thread_alive;
    blackstar_ctrl_t * ctrl_arr;
}pthread_shared_t;

extern blackstar_t g_blackstar;
extern pthread_shared_t shared_resources;

extern pthread_t footswitch_push_thread;
extern pthread_attr_t footswitch_push_thread_attr; 

extern pthread_t footswitch_pull_thread;
extern pthread_attr_t footswitch_pull_thread_attr; 

extern pthread_t footswitch_evt_thread;
extern pthread_attr_t footswitch_evt_thread_attr; 

blackstar_err_t blackstar_init      ( blackstar_t * blackstar );
blackstar_err_t blackstar_deinit    ( blackstar_t * blackstar );
blackstar_err_t blackstar_set_ctrl  ( blackstar_t * blackstar, blackstar_ctrl_name_t ctrl_name, double human_val );
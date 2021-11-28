#include <stdio.h> 
#include <wchar.h> 
#include <inttypes.h>
#include <string.h>

#include "hidapi.h"

#define MAX_STR         255
#define HID_PACK_SIZE   64
#define VENDOR_ID       0x27d4
#define PRODUCT_ID      0x0012

#define BLACKSTAR_INSTANCE          &(g_blackstar)

#define DO_NOTHING
#define ASSERT_IF_FALSE(con)        RET_ERR_IF_FALSE(con, BLACKSTAR_ERROR_ASSERT)
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
    BLACKSTAR_ERROR_IO
}blackstar_err_t;

typedef enum blackstar_ctrl_name
{
    BLACKSTAR_CTRL_NAME_VOICE  =  0x01
} blackstar_ctrl_name_t;

typedef struct blackstar_ctrl
{
    blackstar_ctrl_name_t ctrl_name;
    uint8_t ctrl_range_dev;
    uint8_t ctrl_range_human;
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

extern blackstar_t g_blackstar;

blackstar_err_t blackstar_init      ( blackstar_t * blackstar );
blackstar_err_t blackstar_deinit    ( blackstar_t * blackstar );
blackstar_err_t blackstar_set_ctrl  ( blackstar_t * blackstar, blackstar_ctrl_name_t ctrl_name, uint8_t val);
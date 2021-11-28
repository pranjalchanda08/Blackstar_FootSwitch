#include "blackstar.h"

blackstar_ctrl_t g_blackstar_ctrl_set[] =
{
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_VOICE,
        .ctrl_range_dev     = 5,
        .ctrl_range_human   = 5,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_GAIN,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_VOLUME,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_BASS,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_MIDDLE,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_TREBLE,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_ISF,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_TVP_VALVE,
        .ctrl_range_dev     = 5,
        .ctrl_range_human   = 5,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_RESONANCE,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_PRESENCE,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_MASTER_VOLUME,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_TVP_SWITCH,
        .ctrl_range_dev     = 1,
        .ctrl_range_human   = 1,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_MOD_SWITCH,
        .ctrl_range_dev     = 1,
        .ctrl_range_human   = 1,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_DELAY_SWITCH,
        .ctrl_range_dev     = 1,
        .ctrl_range_human   = 1,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_REVERB_SWITCH,
        .ctrl_range_dev     = 1,
        .ctrl_range_human   = 1,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_MOD_TYPE,
        .ctrl_range_dev     = 3,
        .ctrl_range_human   = 3,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_MOD_SEGVAL,
        .ctrl_range_dev     = 31,
        .ctrl_range_human   = 31,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_MOD_MANUAL,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_MOD_LEVEL,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_MOD_SPEED,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10.0,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_DELAY_TYPE,
        .ctrl_range_dev     = 3,
        .ctrl_range_human   = 3,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_DELAY_FEEDBACK,
        .ctrl_range_dev     = 31,
        .ctrl_range_human   = 31,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_DELAY_LEVEL,
        .ctrl_range_dev     = 5,
        .ctrl_range_human   = 5,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_DELAY_TIME_COARSE,
        .ctrl_range_dev     = 7,
        .ctrl_range_human   = 7,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_REVERB_TYPE,
        .ctrl_range_dev     = 3,
        .ctrl_range_human   = 3,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_REVERB_SIZE,
        .ctrl_range_dev     = 31,
        .ctrl_range_human   = 31,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_REVERB_LEVEL,
        .ctrl_range_dev     = 127,
        .ctrl_range_human   = 10,
        .ctrl_curr_val      = 0
    },
    {
        .ctrl_name          = BLACKSTAR_CTRL_NAME_FX_FOCUS,
        .ctrl_range_dev     = 3,
        .ctrl_range_human   = 3,
        .ctrl_curr_val      = 0
    },
};

const uint8_t g_blackstar_ctrl_set_size = sizeof(g_blackstar_ctrl_set)/sizeof(blackstar_ctrl_t);

pthread_t footswitch_push_thread;
pthread_attr_t footswitch_push_thread_attr; 

pthread_t footswitch_pull_thread;
pthread_attr_t footswitch_pull_thread_attr; 

pthread_t footswitch_evt_thread;
pthread_attr_t footswitch_evt_thread_attr; 

pthread_shared_t shared_resources = 
{
    .thread_alive  = 1,
    .ctrl_arr      = g_blackstar_ctrl_set,
};
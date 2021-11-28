#include "blackstar.h"

static uint8_t _parse_human_to_dev (blackstar_ctrl_t * ctrl_request, double human_val);
static void _cleanup_hid (hid_device *handle);

blackstar_t g_blackstar;
extern blackstar_ctrl_t g_blackstar_ctrl_set[];
extern const uint8_t g_blackstar_ctrl_set_size;

blackstar_err_t blackstar_init( blackstar_t * blackstar )
{
    uint16_t u16_res;
    
    struct hid_device_info *info = NULL, *ptr = NULL;

    ASSERT_IF_FALSE(blackstar->is_connected == 0);

    u16_res = hid_init();
    RET_ERR_IF_FALSE(u16_res == BLACKSTAR_SUCCESS, BLACKSTAR_ERROR);

    blackstar->device = hid_open(VENDOR_ID, PRODUCT_ID, NULL);
    if(blackstar->device == NULL)
    {
        _cleanup_hid(blackstar->device);
        return BLACKSTAR_ERROR;
    }

    u16_res = hid_get_manufacturer_string(blackstar->device, blackstar->man_str, MAX_STR);
    RET_ERR_IF_FALSE(u16_res == BLACKSTAR_SUCCESS, BLACKSTAR_ERROR);

    u16_res = hid_get_product_string(blackstar->device, blackstar->prod_str, MAX_STR);
	RET_ERR_IF_FALSE(u16_res == BLACKSTAR_SUCCESS, BLACKSTAR_ERROR);

    blackstar->is_connected = 1;

    return BLACKSTAR_SUCCESS;
}

blackstar_err_t blackstar_set_ctrl  ( blackstar_t * blackstar, blackstar_ctrl_name_t ctrl_name, double human_val )
{
    RET_ERR_IF_FALSE(ctrl_name != BLACKSTAR_CTRL_NAME_DELAY_TIME, BLACKSTAR_ERROR_NOT_SUPPORTED);

    blackstar_ctrl_t * ctrl_request;
    uint8_t search_flag = 0;
    uint8_t dev_val = 0;

    for(int i = 0; i < g_blackstar_ctrl_set_size; i++)
    {
        if(g_blackstar_ctrl_set[ i ].ctrl_name == ctrl_name)
        {
            ctrl_request = (blackstar_ctrl_t *) &(g_blackstar_ctrl_set[ i ]);
            search_flag = 1;
            break;
        }
    }

    RET_ERR_IF_FALSE(search_flag == 1, BLACKSTAR_ERROR_NOT_SUPPORTED);
    ASSERT_IF_FALSE(human_val <= ctrl_request->ctrl_range_human);

    dev_val = _parse_human_to_dev(ctrl_request, human_val);

    uint16_t res;
    memset(blackstar->u8_push_pull, 0, HID_PACK_SIZE);

    blackstar->u8_push_pull[0] = BLACKSTAR_CMD_CTRL;
    blackstar->u8_push_pull[1] = ctrl_request->ctrl_name;
    blackstar->u8_push_pull[2] = 0x00;
    blackstar->u8_push_pull[3] = 0x01;
    blackstar->u8_push_pull[4] = dev_val;
    
    res = hid_write(blackstar->device, blackstar->u8_push_pull, HID_PACK_SIZE);
    RET_ERR_IF_FALSE(res != -1, BLACKSTAR_ERROR_IO);

    return BLACKSTAR_SUCCESS;
}

blackstar_err_t blackstar_deinit( blackstar_t * blackstar )
{
    _cleanup_hid(blackstar->device);

    if(blackstar->is_connected)
        blackstar->is_connected = 0;

    return BLACKSTAR_SUCCESS;
}

static uint8_t _parse_human_to_dev (blackstar_ctrl_t * ctrl_request, double human_val)
{
    return (uint8_t) ((human_val * ctrl_request->ctrl_range_dev) / ctrl_request->ctrl_range_human);
}

static void _cleanup_hid(hid_device *handle)
{
    if(handle != NULL)
        hid_close(handle);
    hid_exit();
}
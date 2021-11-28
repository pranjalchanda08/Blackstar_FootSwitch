#include "blackstar.h"

wchar_t u8_buff[MAX_STR + 1];
uint8_t u8_push_pull[ HID_PACK_SIZE + 1];

static void _cleanup_hid(hid_device *handle);

blackstar_t g_blackstar;

int main(int argc, char* argv[])
{
    blackstar_err_t res;
    hid_device *handle;

    res = blackstar_init(BLACKSTAR_INSTANCE);
    if(!res)
    {
        blackstar_set_ctrl(BLACKSTAR_INSTANCE, BLACKSTAR_CTRL_NAME_VOICE, 5);
    }
    
    blackstar_deinit(BLACKSTAR_INSTANCE);
    return 0;
}

blackstar_err_t blackstar_init( blackstar_t * blackstar )
{
    uint16_t u16_res;
    
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

    return BLACKSTAR_SUCCESS;

}

blackstar_err_t blackstar_set_ctrl  ( blackstar_t * blackstar, blackstar_ctrl_name_t ctrl_name, uint8_t val)
{
    uint16_t res;
    memset(blackstar->u8_push_pull, 0, HID_PACK_SIZE);

    blackstar->u8_push_pull[0] = 0x03;
    blackstar->u8_push_pull[1] = ctrl_name;
    blackstar->u8_push_pull[2] = 0x00;
    blackstar->u8_push_pull[3] = 0x01;
    blackstar->u8_push_pull[4] = val;
    res = hid_write(blackstar->device, blackstar->u8_push_pull, HID_PACK_SIZE);
    
}
blackstar_err_t blackstar_deinit( blackstar_t * blackstar )
{
    _cleanup_hid(blackstar->device);

    return BLACKSTAR_SUCCESS;
}

static void _cleanup_hid(hid_device *handle)
{
    if(handle != NULL)
        hid_close(handle);
    hid_exit();
}
#include "remote_control.h"
/*遥控器的模块层*/
rc_ctrl_t rc_ctrl;

static void sbus_to_rc(uint8_t *sbus_buff)
{
    rc_ctrl.rocker_right_x=((sbus_buff[0]|sbus_buff[1]<<8)&0x07FF)-RC_CH_OFFSET;
    rc_ctrl.rocker_right_y=((sbus_buff[1]>>3|sbus_buff[2]<<5)&0x07FF)-RC_CH_OFFSET;
    rc_ctrl.rocker_left_x=((sbus_buff[2]>>6|sbus_buff[3]<<2|sbus_buff[4]<<10)&0x07FF)-RC_CH_OFFSET;
    rc_ctrl.rocker_left_y=((sbus_buff[4]>>1|sbus_buff[5]<<7)&0x07FF)-RC_CH_OFFSET; 
    rc_ctrl.switch_left=(sbus_buff[5]>>4)&0x0003;
    rc_ctrl.switch_right=((sbus_buff[5]>>4)&0x000C)>>2;
}


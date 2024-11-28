#include "DJMotor.h"
#include "stdlib.h"

int idx=0;
static DJMotor_INSTANCE_t *djmotor_instance[DJMotor_num]={NULL};

static CAN_INSTANCE_t send_to_can[6]=/*发报文*/
{
    NULL,
};

void DJMotor_Stop(DJMotor_INSTANCE_t *motor)/*使电机暂停*/
{
    motor->motor_setting.motor_enable_flag=MOTOR_STOP;
}

void DJMotor_Enanble(DJMotor_INSTANCE_t *motor)/*使能：启用*/
{
    motor->motor_setting.motor_enable_flag=MOTOR_ENABLE;
}

void DJMotor_outerloop(DJMotor_INSTANCE_t *motor,close_loop_type_e outer_loop)
{
    motor->motor_setting.outer_loop_type=outer_loop;
}

void DJMotor_Changefeed(DJMotor_INSTANCE_t *motor,feedback_source_e source,close_loop_type_e loop)
{
    if(loop==ANGLE_LOOP)
    motor->motor_setting.angle_feedback_source=source;
    else if(loop==SPEED_LOOP)
    motor->motor_setting.speed_feedback_source=source;    
}

void DJMotor_set(DJMotor_INSTANCE_t *motor,float set)
{
    motor->motor_controller.set=set;
}

void Decode_DJMotor(CAN_INSTANCE_t *instance)
{/*填入反馈信息的具体代码*/
    uint8_t *rxbuff=instance->rx_buff;
    DJMotor_INSTANCE_t *motor = (DJMotor_INSTANCE_t *)instance->id;
    motor->measure.ecd=(uint16_t)(rxbuff[0]<<8)|rxbuff[1];
    motor->measure.last_ecd=motor->measure.ecd;
    motor->measure.angle_round=motor->measure.ecd*ECD_TO_ANGLE;
    motor->measure.speed_aps=(1-SPEED_SMOOTH_COEF)*(float)((uint16_t)rxbuff[2]<<8|rxbuff[3])+SPEED_SMOOTH_COEF*(motor->measure.speed_aps);   
    motor->measure.real_current=(1-CURRENT_SMOOTH_COEF)*(float)((uint16_t)rxbuff[4]<<8|rxbuff[5])+CURRENT_SMOOTH_COEF*(motor->measure.real_current);   
    motor->measure.temperature=rxbuff[6];
    if( motor->measure.ecd- motor->measure.last_ecd<-4096)/*计算总圈数*/
    motor->measure.angle_round++;
    else if( motor->measure.ecd- motor->measure.last_ecd>4096)
    motor->measure.angle_round--;
    motor->measure.total_angle=motor->measure.angle_round*360+motor->measure.angle_round;
}

DJMotor_INSTANCE_t *DJMotorInit(motor_init_instance_t *config)
{
    DJMotor_INSTANCE_t *instance= (DJMotor_INSTANCE_t* ) malloc(sizeof(DJMotor_INSTANCE_t));
    memset(instance,0,sizeof(DJMotor_INSTANCE_t));

    instance->motor_type=config->motor_type;
    instance->motor_setting.motor_reverse_flag=config->motor_setting_config.motor_reverse_flag;

    PID_Init(&instance->motor_controller.speed_pid,&config->pid_init_config.speed_pid);
    PID_Init(&instance->motor_controller.angle_pid,&config->pid_init_config.angle_pid);
    PID_Init(&instance->motor_controller.current_pid,&config->pid_init_config.current_pid);

    instance->motor_controller.other_angle_feedback_ptr=config->pid_init_config.other_angle_feedback_ptr;
    instance->motor_controller.other_angle_feedback_ptr=config->pid_init_config.other_speed_feedback_ptr;

    config->can_init_config.id=instance;

    instance->motor_can_instance=Can_Register(&config->can_init_config);
    DJMotor_Enanble(instance);
    djmotor_instance[idx++]=instance;
    return instance;
}

void DJMotor_control()/*发送电机报文：电机控制*/
{
    DJMotor_INSTANCE_t *motor;
    motor_setting_t *motor_setting;
    DJMotor_Measure_t *measure;
    pid_controller_t *motor_pid;
    float pid_set,pid_measure;
    int16_t messeage_num=motor->motor_can_instance->tx_id-0x201;
    int16_t set;
    for(size_t i=0;i<idx;++i)/*遍历所有电机：计算完pid统一发送*//*idx表示有几个电机*/
    {
        motor=djmotor_instance[i];
        motor_setting=&motor->motor_setting;
        measure=&motor->measure;
        motor_pid=&motor->motor_controller;
        pid_set=motor_pid->set;

        if(motor_setting->motor_reverse_flag==MOTOE_REVERSE)
        pid_set*=-1;

        if((motor_setting->close_loop_type&ANGLE_LOOP)&&(motor_setting->outer_loop_type==ANGLE_LOOP))
        {
            if(motor_setting->angle_feedback_source==OTHER_FEED)
                pid_measure=*motor_pid->other_angle_feedback_ptr;
            else
                pid_measure=measure->angle_round;
            pid_set=PID_Calculate(&motor_pid->angle_pid,pid_set,pid_measure);
        }
        if((motor_setting->close_loop_type&SPEED_LOOP)&&(motor_setting->outer_loop_type==ANGLE_LOOP|SPEED_LOOP))
        {
            if(motor_setting->angle_feedback_source==OTHER_FEED)
                pid_measure=*motor_pid->other_speed_feedba ck_ptr;
            else
                pid_measure=measure->speed_aps;
            pid_set=PID_Calculate(&motor_pid->speed_pid,pid_set,pid_measure);
        }
        if(motor_setting->close_loop_type&CURRENT_LOOP)
        {
            pid_set=PID_Calculate(&motor_pid->current_pid,pid_set,pid_measure);
        }
            set=(int16_t)pid_set;
    }
    send_to_can[0].tx_buff[2*messeage_num]=(uint8_t)(set>>8);/*开始发报文*/
    send_to_can[0].tx_buff[2*messeage_num+1]=(uint8_t)(set&0x00ff);

    if(motor->motor_setting.motor_enable_flag==MOTOR_STOP)
    {
        memset(send_to_can[0].tx_buff+2*messeage_num,0,16u);
    }
}
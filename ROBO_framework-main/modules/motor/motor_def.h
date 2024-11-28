#ifndef MOTOR_DEF_H
#define MOTOR_DEF_H
#include "pid.h"
#include "can.h"
typedef enum
{/*指令处理*/
    OPEN_LOOP=0b0000,/*二进制*//*开环闭环：用不用二进制*/
    SPEED_LOOP=0b0001,/*速度环*/
    ANGLE_LOOP=0b0010,/*角度环*/
    CURRENT_LOOP=0b0100,
    SPEED_ANGLE_LOOP=0b0011,
    SPEED_CURRENT_LOOP=0b0101,
    ANGLE_CURRENT_LOOP=0b0110,
    ALL_LOOP=0b0111,
}close_loop_type_e;

typedef enum/*指令反馈*/
{
    MOTOR_FEED=0,
    OTHER_FEED,
}feedback_source_e;

typedef enum/*电机正反转动*/
{
    MOTOR_NORMAL=0,
    MOTOR_REVERSE,/*反转的标志*/
}motor_reverse_flag_e;

typedef enum/*电机的反馈来源*/
{
    MOTOR_STOP=0,
    MOTOR_ENABLE,
}motor_enable_flag_e;

typedef enum
{/*电机类型*/
    NONE=0,
    GM6020,
    M3508,/*底盘*/
    M2006,
}motor_type_e;

typedef struct 
{
    close_loop_type_e outer_loop_type;
    close_loop_type_e close_loop_type;
    feedback_source_e angle_feedback_source;
    feedback_source_e speed_feedback_source;
    motor_reverse_flag_e motor_reverse_flag;
    motor_enable_flag_e motor_enable_flag;
}motor_setting_t;

typedef struct 
{
    float *other_angle_feedback_ptr;/*其他的反馈来源*/
    float *other_speed_feedback_ptr;/*角速度 速度*/

    PID_instance_t current_pid;
    PID_instance_t speed_pid;
    PID_instance_t angle_pid;

    float set;
}pid_controller_t;/*电机控制器*/

typedef struct 
{
    float *other_angle_feedback_ptr;
    float *other_speed_feedback_ptr;

    PID_init_config_t current_pid;
    PID_init_config_t speed_pid;
    PID_init_config_t angle_pid;
}pid_init_controller_t;

typedef struct
{
    pid_init_controller_t pid_init_config; 
    motor_setting_t motor_setting_config;
    motor_type_e motor_type;
    CAN_INIT_INSTANCE_t can_init_config;
}motor_init_instance_t;



#endif // !MOTOR_DEF_H
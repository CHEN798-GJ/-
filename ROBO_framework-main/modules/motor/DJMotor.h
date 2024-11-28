#ifndef DJMotor_H
#define DJMotor_H
#include "motor_def.h"
#include "stdint.h"
#define ECD_TO_ANGLE (360/8192)/*总共是8192，得到角度值*/
#define SPEED_SMOOTH_COEF 0.05
#define CURRENT_SMOOTH_COEF 0.05
#define DJMotor_num 12
typedef struct /*填入反馈信息*/
{
    uint8_t ecd;/*角度*/
    uint8_t last_ecd;/*上一次的角度*/
    uint8_t angle_round;/*？？？*/
    float speed_aps;/*转速*/
    float real_current;/*电流*/
    float temperature;/*温度*/
    float total_angle;/*总角度，用于计算热量*/
    float init_angle;/*初始化的角度*/
    int32_t total_round;/*总圈数*/
}DJMotor_Measure_t;/*电机的测量值*/

typedef struct
{
    DJMotor_Measure_t measure;
    motor_setting_t motor_setting;
    pid_controller_t motor_controller;
    CAN_INSTANCE_t *motor_can_instance;
    motor_type_e motor_type;

    uint8_t sender_group;
}DJMotor_INSTANCE_t;
/*写完.c文件之后对函数进行声明*/
void DJMotor_Stop(DJMotor_INSTANCE_t *motor);
void DJMotor_Enanble(DJMotor_INSTANCE_t *motor);
void DJMotor_outerloop(DJMotor_INSTANCE_t *motor,close_loop_type_e outer_loop);
void DJMotor_Changefeed(DJMotor_INSTANCE_t *motor,feedback_source_e source,close_loop_type_e loop);
void DJMotor_set(DJMotor_INSTANCE_t *motor,float set);
void Decode_DJMotor(CAN_INSTANCE_t *instance);
DJMotor_INSTANCE_t *DJMotorInit(motor_init_instance_t *config);
void DJMotor_control();

#endif // !DJMotor_H
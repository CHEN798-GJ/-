#include "pid.h"

static void pidout_limit(PID_instance_t *pid)
{
    if(pid->output>pid->maxout)
    pid->output=pid->maxout;
    else if(pid->output<-pid->maxout)
    pid->output=-pid->maxout;
    else
    pid->output=pid->output;
}
void PID_Init(PID_instance_t *pid,PID_init_config_t *pid_init)
{
    memset(pid,0,sizeof(PID_instance_t));
    memcpy(pid,pid_init,sizeof(PID_init_config_t));
}

float PID_Calculate(PID_instance_t *pid,float set,float measure)
{
/*
error=set-measure
pout=kp*error；
dout=kd（error-last_error）/t;
iout+=ki*error*t;
output=pout+iout+dout*/
    pidout_limit(pid);

    pid->measure=measure;
    pid->last_measure=pid->measure;
    pid->set=set;
    pid->err=pid->set-pid->measure;

    pid->last_err=pid->err;

    pid->Pout=pid->kp*pid->err;
    pid->Iout+=pid->ki*pid->err*pid->dt;
    pid->Dout=pid->kd*(pid->err-pid->last_err)/pid->dt;
    pid->output=pid->Pout+pid->Iout+pid->Dout;
    pid->last_output=pid->output;

    return pid->output;
}







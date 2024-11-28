#include "can.h"//框架文件
#include "stddef.h"
static CAN_INSTANCE_t *can_instance[CAN_MX_Register]={NULL};
int16_t idx=0;

CAN_INSTANCE_t *Can_Register(CAN_INIT_INSTANCE_t *config)
{
    CAN_INSTANCE_t *instance= (CAN_INSTANCE_t* ) malloc(sizeof(CAN_INSTANCE_t));
    memset(instance,0,sizeof(CAN_INSTANCE_t));

    instance->tx_id=config->tx_id;
    instance->rx_id=config->rx_id;
    instance->id=config->id;
    can_instance[idx++]=instance;
    return instance;
}
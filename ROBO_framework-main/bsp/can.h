#ifndef CAN_H
#define CAN_H
#include "stdint.h"

#define CAN_MX_Register 4
#define NULL 0
typedef struct
{
    uint32_t tx_id;
    uint32_t rx_id;
    uint8_t  tx_buff[8];
    uint8_t  rx_buff[8];
    uint32_t rx_len;
    void *id;
}CAN_INSTANCE_t;

typedef struct
{
    uint32_t tx_id;
    uint32_t rx_id;
    void *id;
   
}CAN_INIT_INSTANCE_t;

CAN_INSTANCE_t *Can_Register(CAN_INIT_INSTANCE_t *config);

#endif // !CAN_H








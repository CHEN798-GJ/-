#include "board_comm.h"
#include "stdlib.h"

//帧头+数据长度+数据帧+帧尾+校验位
BOARD_CANcomm_INSTANCE *board_comm_init(BOARD_INIT_CANcomm_INSTANCE *config)
{
    BOARD_CANcomm_INSTANCE *board_comm= (BOARD_CANcomm_INSTANCE* ) malloc(sizeof(BOARD_CANcomm_INSTANCE));
    memset(board_comm,0,sizeof(BOARD_CANcomm_INSTANCE));

    board_comm->recv_buff_len=config->recv_buff_len;
    board_comm->send_buff_len=config->send_buff_len;
    board_comm->recv_data_len=config->recv_data_len;
    board_comm->send_data_len=config->send_data_len;
    board_comm->raw_send_buff[0]=CAN_COMM_HEADER;
    board_comm->raw_send_buff[1]=config->send_data_len;
    board_comm->raw_send_buff[config->send_data_len+CAN_COMM_OFFSET_BYTES-1]=CAN_COMM_TAIL;
    config->can_config.id =board_comm;
    board_comm->board_can_comm=Can_Register(&config->can_config);
    return board_comm;
}

void BOARD_can_send(BOARD_CANcomm_INSTANCE *instance,uint8_t *data)
{   
    memcpy(instance->raw_send_buff+ 2 ,data,instance->send_data_len);
    for(size_t i=0;i<instance->send_buff_len;i+=8)
    {
        
    }
}

void *Board_CAN_Get(BOARD_CANcomm_INSTANCE *instance)
{
    instance->update_flag=0;
    return instance->unpacked_recv_buff;
}



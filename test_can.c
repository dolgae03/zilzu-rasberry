/* RaspberryPi 4 for Automotive IoT Kit
 * TITLE : C Based Example for CAN
 * File  : can_ex1.c
 * Auth  : wikipedia.org
 * Ment  : Original Soruce - http://en.wikipedia.org/wiki/SocketCAN */

/* 고정IP를 설정 후 Visual Studio에서 여는 방법
터미널 실행 후 pi@raspberruypi : ~/ 에서 cd Desktop/ test 입력 후 바뀐 디렉토리에서 g++ -o main test.c 를 실행 시 디버깅됨.
다른 사용자에게 업데이트 : 그냥 일정 시간이 지나면 업데이트가 됨.
업데이트가 된 이후 터미널에 g++ -E main test.c 실행 후 g++ -S main test.c 실행하여 디버깅.
CAN 통신 열기 - sudo ip link can0 up type can bitrate 250000
*/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <net/if.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>

#include <linux/can.h>
#include <linux/can/raw.h>


#define MCU_ID 0x0C01EFD0
#define VCU_ID_1 0x1801D0EF //vcan에서 열었을 때는 0x180117EF
#define VCU_ID_2 0x1802D0EF
uint16_t TargetPhaseCurrent01A;
uint16_t TargetSpeedRPM;
uint8_t controlCmd;
uint8_t LiveCounter;



//ERROR_CODE : manual에서 나와있는 System에서 문제가 생기는 22개의 문제들에 대해 나와있음.

enum ERROR_CODE {
    Over = 0,
    Overcurrent,
    Overload,
    Overvoltage,
    dfs,
    Undervoltage,
    ControllerOverheat,
    MotorOverheat,
    MotorStalled,
    MotorOutofphase,
    MotorSensor,
    MotorAUXSensor,
    EncoderMisaligned,
    AntiRunawayEngaged,
    MainAccelerator,
    AUXAccelerator,
    Precharge,
    DCContactor,
    Powervalve,
    CurrentSensor,
    Autotune,
    RS485,
    CAN,
    Software  
};

// 모터에서 계속 받는 기본적인 값들//
struct MCU_SEND_1{
    int rpmSpeed;
    double BUS_Voltage, BUS_Current, Phase_Current;
}; // Motor Control Unit Sends Part 1에서 받는 네 가지 값.

struct MCU_SEND_2{
    int8_t Controller_Temperature, Motor_Temperature, Accelerator_Opening, Gear, Brake, Operation_Mode, DC_Contactor, life_signal;
    //bool running, mode;
    bool error[24];
    // Motor Control Unit Sends Part 2에서 받는 값과 에러
};


// Vehicle Control Unit Sends 에서 보내는 값 -> 새로운 pdf에서 VCU에 관한 얘기가 없으므로 보류(2023.05.22 01:11)
// struct can_frame *
// VCU_SEND(uint16_t target_torque, uint16_t target_speed, uint16_t accelerator, uint8_t Gear, uint8_t Brake, uint8_t Operation_Mode, uint8_t DC_Contactor,uint8_t life_signal, int socket_fd){ 
//     struct can_frame * frame = (struct can_frame *) malloc(sizeof(struct can_frame));
//     //char gear, int brake, int mode, int contactor,
//     frame -> can_id = MCU_ID & 0x1fffffff;
//     frame -> can_id |= (1<<31);

//     *((uint16_t *)(&(frame -> data[0]))) = (target_torque + 3200) * 10;
//     *((uint16_t *)(&(frame -> data[2]))) = target_speed + (32000);
//     //*((uint16_t *)(&(frame -> data[3]))) = target_speed + (32000);
//     //frame -> data[4] = (uint8_t)((running << 1) | (!!mode));
//     frame -> data[7] = life_signal;
    
//     printf("%u %u %u\n", target_torque, target_speed, frame -> data[4] );
    
//     int nbytes = write(socket_fd, frame, sizeof(struct can_frame));
//     printf("send : %d\n",nbytes);
    
//     free(frame);
    
//     return NULL;
// }

struct can_frame *
VCU_SEND(uint16_t target_torque, uint16_t target_speed, int running, int mode, uint8_t life_signal, int socket_fd){ 
    struct can_frame * frame = (struct can_frame *) malloc(sizeof(struct can_frame));
    
    frame -> can_id = MCU_ID & 0x1fffffff;

    printf("%p\n",frame->can_id);
    frame -> can_id |= (1<<31);
    frame -> can_dlc = 8;

    //*((uint16_t *)(&(frame -> data[0]))) = (target_torque + 3200) * 10;
    //*((uint16_t *)(&(frame -> data[2]))) = target_speed + (32000);
    *((uint16_t *)(&(frame -> data[0]))) = target_torque;
    *((uint16_t *)(&(frame -> data[2]))) = target_speed;
    frame -> data[4] = (uint8_t)((mode << 1) | (!!running));
    frame -> data[7] = life_signal;
    
    printf("%u %u %u\n", *((uint16_t *)(&(frame -> data[0]))), *((uint16_t *)(&(frame -> data[2]))), frame -> data[4] );
    
    int nbytes = write(socket_fd, frame, sizeof(struct can_frame));
    printf("send : %d\n",nbytes);
    
    free(frame);
    
    return NULL;
}

struct MCU_SEND_1 * //bus voltage / bus current / phase current / rpm 출력
MCU_RECEIVE_1(struct can_frame * frame){
    struct MCU_SEND_1 * data = (struct MCU_SEND_1 *) malloc(sizeof(struct MCU_SEND_1));

    data -> BUS_Voltage = (*((uint16_t *)(&(frame -> data[0])))) * 0.1;
    data -> BUS_Current = (*((uint16_t *)(&(frame -> data[2])))) * 0.1 - 3200.0;
    data -> Phase_Current = (*((uint16_t *)(&(frame -> data[4])))) * 0.1 - 3200.0;
    data -> rpmSpeed = (*((uint16_t *)(&(frame -> data[6])))) - 32000;
    
    /*모터 컨트롤로부터 받는 데이터의 0,1은 Bus voltage, 2,3은 Bus current, 4,5는 Phase current, 6,7은 Speed이므로 이 값을 받아서 계산한다.
     *  또한 bit당 resolution이 0.1/0.1/0.1/1인 것으로부터, 각각 계산을 해주며, 추가적으로 범위에 맞추어서 offset을 진행한다.*/ 
    printf("%lf %lf %lf %d\n",data -> BUS_Voltage, data -> BUS_Current, data -> Phase_Current, data->rpmSpeed); 
    //첫 줄 - bus voltage / bus current / phase current / rpm 출력

    return data;
}

// struct MCU_SEND_2 *
// MCU_RECEIVE_2(struct can_frame * frame){
//     struct MCU_SEND_2 * data = (struct MCU_SEND_2 *) malloc(sizeof(struct MCU_SEND_2));

//     data -> Controller_Temperature = -40 + (frame -> data[0]);
//     data -> Motor_Temperature = -40 + (frame -> data[1]);
//     data -> Accelerator_Opening = (frame -> data[2]); // 새로운 datasheet에서 나온 Accelerator 값
    
//     uint8_t Gear;
//     uint8_t Brake;
//     uint8_t Operation_Mode;
//     uint8_t DC_Contactor;
//     frame -> data[3] = (uint8_t)((Gear<<5) | (Brake<<4) || (Operation_Mode<<1) | (!!DC_Contactor));
    

//     printf("%d %d %d %d %d %d %d\n", data->Controller_Temperature, data->Motor_Temperature, data -> Accelerator_Opening, 
//     data -> Gear, data -> Brake, data -> Operation_Mode, data -> DC_Contactor); 
//     //두 번째 줄에서 컨트롤러와 모터의 온도, 그리고 쓰로틀 페달 밟은 정도를 출력
    

//     uint8_t temp;
//     temp = frame -> data[5];
//     for(int i=23; i>=16; i--){
//         data->error[i] = (temp & 1);
//         //printf("%d : %d\n",i, data->error[i]);
//         temp = temp >> 1;
//     }
//     temp = frame -> data[4];
//     for(int i=15; i>=8; i--){
//         data->error[i] = (temp & 1);
        
//         //printf("%d : %d\n",i, data->error[i]);
//         temp = temp >> 1;
//     }
//     temp = frame -> data[3];
//     for(int i=7; i>=0; i--){
//         data->error[i] = (temp & 1);
        
//         //printf("%d : %d\n",i, data->error[i]);
//         temp = temp >> 1;
//     }

//     data -> life_signal = frame -> data[7];
//     data -> life_signal=1;

//     return data;
// }

struct MCU_SEND_2 *
MCU_RECEIVE_2(struct can_frame * frame){
    struct MCU_SEND_2 * data = (struct MCU_SEND_2 *) malloc(sizeof(struct MCU_SEND_2));

    data -> Controller_Temperature = -40 + (frame -> data[0]);
    data -> Motor_Temperature = -40 + (frame -> data[1]);
    
    char c = frame ->data[2];

    printf("%d %d %d\n", data->Controller_Temperature, data->Motor_Temperature, c); //두 번째 줄에서 컨트롤러와 모터의 온도를 출력
    

    uint8_t temp;
    temp = frame -> data[5];
    for(int i=23; i>=16; i--){
        data->error[i] = (temp & 1);
        //printf("%d : %d\n",i, data->error[i]);
        temp = temp >> 1;
    }
    temp = frame -> data[4];
    for(int i=15; i>=8; i--){
        data->error[i] = (temp & 1);
        
        //printf("%d : %d\n",i, data->error[i]);
        temp = temp >> 1;
    }
    temp = frame -> data[3];
    for(int i=7; i>=0; i--){
        data->error[i] = (temp & 1);
        
        //printf("%d : %d\n",i, data->error[i]);
        temp = temp >> 1;
    }

    data -> life_signal = frame -> data[7];
    int a = data->life_signal;
    printf("%d\n", a);

    return data;
}



/*void VCU_SendCommand(void){
    
    CAN_init();
    CAN_HandleTypeDef hcan1;
    CAN_TxHeaderTypeDef TxHeader;
    CAN_RXHeaderTypeDef RxHeader;
    
    uint8_t TxData[8];
    uint8_t RxData[8];
    
    
    uint32_t TxMailbox;
    uint8_t TxBuf[8];
    TxBuf[0]=(uint8_t)(TargetPhaseCurrent01A);
    TxBuf[1]=(uint8_t)(TargetPhaseCurrent01A>>8);
    TxBuf[2]=(uint8_t)(TargetSpeedRPM);
    TxBuf[3]=(uint8_t)(TargetSpeedRPM>>8);
    TxBuf[4]=ControlCmd;
    TxBuf[5]=0;
    TxBuf[6]=0;
    TxBuf[7]=LiveCounter;;
    
    CAN_TxHeader.ExtId=0x0C01EFD0;
    CAN_TxHeader.IDE=CAN_ID_EXT;
    CAN_TxHeader.RTR=CAN_RTR_DATA;
    CAN_TxHeader.DLC=8;
    CAN_TxHeader.TransmitGlobalTime=DISABLE;
    HAL_CAN_AddTxMessageCANxHandle,&CAN_TxHeader,TxBuf,&TxMailbox;
}*/

//Handshake에 관한 코드. 변경금지
int can_handshake(int socket_fd){
    struct can_frame * frame = (struct can_frame *) malloc(sizeof(struct can_frame));
    int nbytes;


    

    printf("handshake in\n");

    while(true){
        nbytes = read(socket_fd, frame, sizeof(struct can_frame));

        frame->can_id = ((frame -> can_id)<<1)>>1;
        //printf("%d %x %x\n",nbytes, frame->can_id, VCU_ID_1);
        if(nbytes == 0){
            printf("data_recieve_fail : handshake\n");
            continue;
        }

        if(frame->can_id != VCU_ID_1){
            printf("can_id is not for handshake\n");
            continue;
        }

        bool key = true;

        for(int i=0;i<8;i++){
            if(frame->data[i] != 0x55){
                key = false;
                break;
            }
        }

        if(!key){
            printf("It is not handshake packet\n");
            continue;
        }

        break;
    }

    frame -> can_id = MCU_ID & 0x1fffffff;
    frame -> can_id |= (1<<31);
    frame -> can_dlc = 8;

    for(int i=0; i<8; i++)
        frame -> data[i] = 0xAA;

    nbytes = write(socket_fd, frame, sizeof(struct can_frame));
    printf("Wrote %d bytes and handshake successs?\n", nbytes);
    free(frame);

    return 0;
}


//변경되는 코드 부분들.
int main(void)
{
    int s;
    int nbytes;
    struct sockaddr_can addr;
    struct can_frame * frame = (struct can_frame *) malloc(sizeof(struct can_frame));
    struct ifreq ifr;
    
    printf("dsafa\n");
    if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) == -1) {
	    perror("Error while opening socket");
	    return -1;
    }

    printf("dsafa\n");
    strcpy(ifr.ifr_name, "can0");
    int ret = ioctl(s, SIOCGIFINDEX, &ifr);
	if(ret < 0){
        perror("ioctl error");
        return -1;
    }

    printf("dsafa\n");
    addr.can_family  = PF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
	    perror("Error in socket bind");
	    return -2;
    }

    struct can_filter rfilter[1];
    rfilter[0].can_id = 0x123;
    rfilter[0].can_mask = CAN_SFF_MASK;

    
    can_handshake(s);

    printf("dsafa");
    //실제로 계속 실행되는 부분
    while(true){    
        struct can_frame * frame = (struct can_frame *) malloc(sizeof(struct can_frame));
        int nbytes;
        uint8_t life_signal = 0;

        nbytes = read(s, frame, sizeof(struct can_frame));
        
        frame->can_id = ((frame -> can_id)<<1)>>1;
        //printf("can_id : %p\n",frame->can_id);
        
        if(frame -> can_id == VCU_ID_2){
            struct MCU_SEND_2 * test = MCU_RECEIVE_2(frame);

            free(test);
        }

        if(frame -> can_id == VCU_ID_1){
            bool hand = false;

            for(int i=0;i<8;i++){
                if(frame -> data[i] != 0x55){    
                    hand = true;
                    break;
                }
            }

            if(!hand){
                can_handshake(s);
                continue;
            }

            //VCU_SEND(55,3500,1,1,life_signal+1,s);
            
           VCU_SEND(5,10,1,1,1,s);
            struct MCU_SEND_1 * test = MCU_RECEIVE_1(frame);
            free(test);
        }
        //VCU_SEND(uint16_t target_torque, uint16_t target_speed, int running, int mode, uint8_t life_signal, int socket_fd)
        


        

        free(frame);
        //printf("Wrote %d bytes\n", nbytes);
    }
    return 0;
}


/*
// CAN 통신을 통하여 컨트롤러에 의도된 값을 보내준다.
int send_to_CAN(void)
{
    int s;
    int nbytes;
    struct sockaddr_can addr;
    struct can_frame * frame = (struct can_frame *) malloc(sizeof(can_frame));
    struct ifreq ifr;
    struct MCU_SEND_1 * data = (struct MCU_SEND_1 *) malloc(sizeof(MCU_SEND_1));
    for (int i=0;i<10;i++){
        (*((uint16_t *)(&frame -> data[6])0)*) = 1500*i;
    data -> rpmSpeed = (*((uint16_t *)(&(frame -> data[6])))) - 32000;
    }
    printf("%d\n", data->rpmSpeed); 
}

*/

/*union SoC_curve (data -> BUS_Voltage){

int A = 1;  int B = 1;
int SoC = SoC_curve (BUS_Voltage);
if (SoC > 20){
    SoC1 = SoC_curve (BUS_Voltage);
    SoC2 = SoC - (BUS_Voltage * BUS_Current * 0.05) / 18000;
    SoC = (A * SoC1 + B * SoC2) / (A+B);
}
printf("%d\n", SoC);

}*/

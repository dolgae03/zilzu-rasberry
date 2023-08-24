import can
import os
import RPi.GPIO as GPIO
import time
import os

can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 250000
from can.interface import Bus

bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate=250000)

class Status:
    def __init__(self, data):
        Gear = {0 : 'N0', 
                1 : 'R',
                2 : 'N',
                3 : 'D1',
                4 : 'D2',
                5 : 'D3',
                6 : 'S',
                7 : 'P'}

        Brake = {0 : False, 1 : True}   
        Operation = {0: 'Stop', 1:'Drive', 2:'Cruise', 3:'EBS', 4:'Hold'}
        DC_Contactor = {0: 'OFF', 1:'ON'}

        data = int.from_bytes(data, byteorder = 'little')

        return

        print(data & (0b111))
        print((data>>3) & (0b1))

        self.Gear = Gear[(data>>5) & (0b111)]
        self.Brake = Brake[(data>>4) & (0b1)]
        self.Opeartion = Operation[(data>>1) & (0b111)]
        self.DC_Contactor = DC_Contactor[(data) & (0b1)]
    
    def __str__(self):
        return '%s|%s|%s|%s' % (self.Gear,self.Brake,self.Opeartion,self.DC_Contactor)


class Error:
    def __init__(self, data):
        
        self.error = []

        data = int.from_bytes(data, byteorder = 'little')

        return

        for key, value in Error.items():
            if ((data >> key) & 1):
                self.error.append(value)
    
    def __str__(self):
        return '|'.join(self.error)


def MCU_RECIEVE_1(data):
    BUS_Voltage = int.from_bytes(data[0:2], byteorder = 'little') * 0.1
    BUS_Current = int.from_bytes(data[2:4], byteorder = 'little') * 0.1 - 3200
    BUS_Phase_Current = int.from_bytes(data[4:6], byteorder = 'little') * 0.1 - 3200 
    BUS_RoationSpeed = int.from_bytes(data[6:8], byteorder = 'little') -32000
    
    return BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed

def MCU_RECIEVE_2(data):
    Controller_Temperture = int.from_bytes(data[0:1], byteorder = 'little') - 40
    Motor_Temperture = int.from_bytes(data[1:2], byteorder = 'little') - 40
    Accelator_Opening = int.from_bytes(data[2:3], byteorder = 'little')

    GearCondition = (int.from_bytes(data[3:4], byteorder='big') >> 5) & 7
    Errorcode = []

    TotalNum = int.from_bytes(data[4:6], byteorder = 'big')
    TotalNum = TotalNum >> 2

    idx = 0

    while TotalNum:
        if TotalNum & 1:
            Errorcode.append(22 - idx)
        
        TotalNum = TotalNum >> 1
    
    Errorcode.reverse()
    Error = '|'.join(Errorcode)

    #return Controller_Temperture, Motor_Temperture, Accelator_Opening, status, error
    return Controller_Temperture, Motor_Temperture, Accelator_Opening, GearCondition, Error


import pygame
from pygame.locals import *


def draw_text_centered(text, center_x, center_y, size):
    font = pygame.font.Font(None, size)  # 지정한 크기의 폰트 생성
    text_surface = font.render(text, True, (255, 255, 255))
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()

    # 텍스트 중심 좌표 계산
    text_x = center_x - text_width // 2
    text_y = center_y - text_height // 2

    screen.blit(text_surface, (text_x, text_y))

def draw_percentage_box(percentage, x, y, width, height):
    pygame.draw.rect(screen, (0, 0, 255), (x, y, width, height), 3)
    fill_height = height * percentage / 100
    pygame.draw.rect(screen, (0, 0, 255), (x, y + height - fill_height, width, fill_height))


def calculateBaterry(consumed_columm):
    Total = 50000
    
    return (Total - consumed_columm) / Total * 100

def main():
    # if os.path.isfile('./Consumed_Colum.txt'):
    #     with open('Consumed_Colum.txt', 'r') as f:
    #         Consumed_Colum = float(f.read())
    # else:
    #     Consumed_Colum = 0

    # write_mode = True
    import datetime

    # 현재 날짜와 시간 가져오기
    current_datetime = datetime.datetime.now()

    # 날짜와 시간을 원하는 형식으로 포맷팅
    yearandday = current_datetime.strftime("%Y_%m_%d")
    now_time = current_datetime.strftime("%H_%M_%S")

    # if not os.path.isfile(f'./can_data_1_{yearandday}.csv'):
    #     with open(f'./can_data_1_{yearandday}.csv', 'w') as f:
    #         f.write('Timestamp,BUS_Voltage(V),BUS_Current(A),BUS_Phase_Current(A),BUS_RoationSpeed(rpm)\n')

    # if not os.path.isfile(f'./can_data_2_{yearandday}.csv'):
    #     with open(f'./can_data_2_{yearandday}.csv', 'w') as f:
    #         f.write('Timestamp,Controller_Teperture(C),Motor_Temperture(C),Accelator_Opening(%),STATUS,ERROR\n')

    
    current_datetime = datetime.datetime.now()

    BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed = 0, 0, 0, 0
    Controller_Temperture, Motor_Temperture, Accelator_Opening = 0, 0, 0

    # pump_control_pin = 20
    # led_control_pin = 21
    # led_status = False

    T, A = [0,0,0,0], [0,0,0,0]
    idx = 0
    bus = Bus()

    pygame.init()

    # 화면 초기화
    display = (800, 480)
    screen = pygame.display.set_mode(display)
    pygame.display.set_caption("Pygame Example")

    # 이미지 로드
    scale = 0.4
    image = pygame.image.load('./map.png')
    image = pygame.transform.scale(image, (int(1327 * scale), int(515 * scale)))  # 이미지 크기 조절

    # 폰트 설정
    font = pygame.font.Font(None, 150)
    clock = pygame.time.Clock()

    import time
    prev_time = time.time()
    write_mode = True

    for msg in bus:
        
        current_datetime = datetime.datetime.now()

        # 날짜와 시간을 원하는 형식으로 포맷팅
        yearandday = current_datetime.strftime("%Y_%m_%d")
        now_time = current_datetime.strftime("%H_%M_%S")

        if msg.arbitration_id == 0x180117EF:
            BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed = MCU_RECIEVE_1(msg.data)

            # T[idx % 4], A[idx % 4] = msg.timestamp, BUS_Current

            # if idx % 4 == 3:
            #     Consumed_Colum += 3 * (0.1) * (A[3] + 3*A[2] + 3*A[1] + A[0]) / 8

            idx += 1

            if write_mode:
                with open(f'can_data_1_{yearandday}.csv', 'a') as file:
                    file.write("{},{},{},{},{},{}\n".format(now_time,msg.timestamp, BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed))


        elif msg.arbitration_id == 0x180217EF:
            Controller_Temperture, Motor_Temperture, Accelator_Opening, GearCond, Error = MCU_RECIEVE_2(msg.data)

            if write_mode:        
                with open(f'can_data_2_{yearandday}.csv', 'a') as f:
                    #f.write("{},{},{},{},{},{}\n".format(msg.timestamp, Controller_Temperture, Motor_Temperture, Accelator_Opening, status, error))
                    f.write("{},{},{},{},{}\n".format(now_time,msg.timestamp, Controller_Temperture, Motor_Temperture, Accelator_Opening))
                    
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return


        # 엑셀 밟은 양

        import math
        Speed = BUS_RoationSpeed / 60 * math.pi * 0.598 * 3.6
        
        draw_text_centered(f"{BUS_RoationSpeed}",230, 480 - 340, 250)
        draw_text_centered(f"RPM",520, 480 - 315, 70)  # 여기에 원하는 값을 입력해주세요.

        # 오른쪽에 사각형 표시 (백분율: 50%)
        # 베터리
        draw_text_centered(f"{BUS_Voltage:.1f}V",685, 480 - 420, 100)
        # Temperture Motor
        
        draw_text_centered(f"M: {Motor_Temperture}'C",150, 480 - 200, 100)
        draw_text_centered(f"C: {Controller_Temperture}'C",420, 480 - 200, 100)
        
        if GearCond == 1:
            draw_text_centered(f"{'R'}",520, 480 - 395, 150)
        else:
            draw_text_centered(f"{'D'}",520, 480 - 395, 150)
        
        #drawBatteryPercentage(30)
        draw_percentage_box(Accelator_Opening, 620, 100, 130, 350)


        draw_text_centered(f"{Speed}",100, 480 - 100, 100)
        draw_text_centered(f"km/h",250, 480 - 100, 100)

        draw_text_centered(f"{Error}",440, 480 - 105, 100)




        # 이미지 표시
        # screen.blit(image, (50, 370 - 135))
        pygame.display.flip()
        pygame.time.wait(10)
            

if __name__ == "__main__":
    main()

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
        Error = {0: 'Overcurrent',1: 'Overload',2: 'Overvoltage',3: 'dfs',4: 'Undervoltage',5: 'ControllerOverheat',6: 'MotorOverheat',7: 'MotorStalled',8: 'MotorOutofphase',9: 'MotorSensor',10: 'MotorAUXSensor',11: 'EncoderMisaligned',12: 'AntiRunawayEngaged',13: 'MainAccelerator',14: 'AUXAccelerator',15: 'Precharge',16: 'DCContactor',17: 'Powervalve',18: 'CurrentSensor',19: 'Autotune',20: 'RS485',21: 'CAN',22: 'Software'}

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

    status = Status(data[3:4])
    error = Error(data[4:6])

    #return Controller_Temperture, Motor_Temperture, Accelator_Opening, status, error
    return Controller_Temperture, Motor_Temperture, Accelator_Opening


import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def drawAccelPercentage(percentage):
    glColor3f(0.3, 0.7, 0.9)  # 사각형 색상 설정 (파란색)
    glBegin(GL_LINE_LOOP)
    glVertex2f(600, 100)    # 왼쪽 아래 꼭지점
    glVertex2f(600, 380)     # 왼쪽 위 꼭지점
    glVertex2f(700, 380)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(700, 100) 
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(600, 100)    # 왼쪽 아래 꼭지점
    glVertex2f(600, 100 + 280 * percentage)     # 왼쪽 위 꼭지점
    glVertex2f(700, 100 + 280 * percentage)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(700, 100)  # 오른쪽 아래 꼭지점 (특정 백분율만큼)
    glEnd()

def drawBettryPercentage(percentage):
    glColor3f(0.3, 0.7, 0.9)  # 사각형 색상 설정 (파란색)
    glBegin(GL_QUADS)

    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(600, 100)    # 왼쪽 아래 꼭지점
    glVertex2f(600, 100 + 280 * percentage)     # 왼쪽 위 꼭지점
    glVertex2f(700, 100 + 280 * percentage)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(700, 100)  # 오른쪽 아래 꼭지점 (특정 백분율만큼)
    glEnd()

def draw_text(Accel, Motor_temp):
    font = pygame.font.Font(None, 36)  # 폰트 설정과 크기 지정
    text_surface = font.render(text, True, (255, 255, 255))  # 텍스트 렌더링
    text_data = pygame.image.tostring(text_surface, "RGBA", True)  # 렌더링한 텍스트 데이터 가져오기

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glRasterPos2f(200, 240)  # 텍스트 위치 설정
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glDisable(GL_BLEND)


def main():

    if os.path.isfile('./Consumed_Colum.txt'):
        with open('Consumed_Colum.txt', 'r') as f:
            Consumed_Colum = float(f.read())
    else:
        Consumed_Colum = 0

    write_mode = True
    BCM_num = 13

    BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed = 0, 0, 0, 0
    Controller_Temperture, Motor_Temperture, Accelator_Opening = 0, 0, 0

    T, A = [0,0,0,0], [0,0,0,0]
    idx = 0

    bus = Bus()

    pygame.init()
    display = (800, 480)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL) #  | FULLSCREEN

    gluOrtho2D(0, 800, 0, 480)  # 2D 뷰포트 설정

    for msg in bus:
        if msg.arbitration_id == 0x180117EF:
            BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed = MCU_RECIEVE_1(msg.data)

            T[idx % 4], A[idx % 4] = msg.timestamp, BUS_Current

            if idx % 4 == 3:
                Consumed_Colum += 3 * (0.1) * (A[3] + 3*A[2] + 3*A[1] + A[0]) / 8

            idx += 1

        elif msg.arbitration_id == 0x180217EF:
            Controller_Temperture, Motor_Temperture, Accelator_Opening = MCU_RECIEVE_2(msg.data)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                

                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT)

        # 왼쪽에 텍스트 표시
        draw_text(f"{BUS_RoationSpeed}")  # 여기에 원하는 값을 입력해주세요.

        # 오른쪽에 사각형 표시 (백분율: 50%)
        percentage = 1  # 여기에 원하는 백분율 값을 입력해주세요. (0 ~ 1 사이 값)
        drawAccelPercentage(Accelator_Opening)
        drawBatteryPercentage(Consumed_Colum)

        pygame.display.flip()

        import time
        test = time.time()
        
        pygame.time.wait(5)
        print(test)

if __name__ == "__main__":
    main()

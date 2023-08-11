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
from PIL import Image
from numpy import array

AccelRefPos = (620, 750)
BatteryRefPos = (650, 750)

def drawAccelPercentage(percentage):
      # 사각형 색상 설정 (파란색)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glColor3f(0.3, 0.7, 0.9)
    glVertex2f(AccelRefPos[0], 50)    # 왼쪽 아래 꼭지점
    glVertex2f(AccelRefPos[0], 350)     # 왼쪽 위 꼭지점
    glVertex2f(AccelRefPos[1], 350)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(AccelRefPos[1], 50) 
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(AccelRefPos[0], 50)    # 왼쪽 아래 꼭지점
    glVertex2f(AccelRefPos[0], 50 + 300 * percentage / 100)     # 왼쪽 위 꼭지점
    glVertex2f(AccelRefPos[1], 50 + 300 * percentage / 100)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(AccelRefPos[1], 50)  # 오른쪽 아래 꼭지점 (특정 백분율만큼)
    glEnd()

def drawBatteryPercentage(Columm_Consumption):
    Battery_Capacity = 240 * 3600

    percentage = (Battery_Capacity - Columm_Consumption) / Battery_Capacity

    glColor3f(0.3, 0.7, 0)  # 사각형 색상 설정 (파란색)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(BatteryRefPos[0], 100)    # 왼쪽 아래 꼭지점
    glVertex2f(BatteryRefPos[0], 250)     # 왼쪽 위 꼭지점
    glVertex2f(BatteryRefPos[1], 250)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(BatteryRefPos[1], 100) 
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(BatteryRefPos[0], 100)    # 왼쪽 아래 꼭지점
    glVertex2f(BatteryRefPos[0], 100 + 150 * percentage / 100)     # 왼쪽 위 꼭지점
    glVertex2f(BatteryRefPos[1], 100 + 150 * percentage / 100)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(BatteryRefPos[1], 100)  # 오른쪽 아래 꼭지점 (특정 백분율만큼)
    glEnd()


def draw_text_centered(text, center_x, center_y, size):
    font = pygame.font.Font(None, size)  # 폰트 설정과 크기 지정
    text_surface = font.render(text, True, (255, 255, 255))  # 텍스트 렌더링
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()

    print(text_width, text_height)

    text_data = pygame.image.tostring(text_surface, "RGBA", True)  # 렌더링한 텍스트 데이터 가져오기

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # 텍스트 중심 좌표 계산
    text_center_x = center_x - text_width / 2
    text_center_y = center_y - text_height / 2

    glRasterPos2f(text_center_x, text_center_y)  # 텍스트 중심 위치 설정
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glDisable(GL_BLEND)

def loadTexture():
    textID = None

    with Image.open("map.png") as text:
        textData = array(list(text.getdata()))
        textID = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, textID)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text.size[0], text.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, textData)
    
    return textID

def drawPicture(centerX, centerY, width, height, textureID):
    half_width = width / 2
    half_height = height / 2
    
    verts = ((half_width, half_height), (half_width, -half_height), (-half_width, -half_height), (-half_width, half_height))
    texts = ((1, 0), (1, 1), (0, 1), (0, 0))
    surf = (0, 1, 2, 3)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textureID)

    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)
    for i in surf:
        glTexCoord2f(texts[i][0], texts[i][1])
        glVertex2f(centerX + verts[i][0], centerY + verts[i][1])
    glEnd()

    glDisable(GL_TEXTURE_2D)


def main():
    if os.path.isfile('./Consumed_Colum.txt'):
        with open('Consumed_Colum.txt', 'r') as f:
            Consumed_Colum = float(f.read())
    else:
        Consumed_Colum = 0

    write_mode = True

    BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed = 0, 0, 0, 0
    Controller_Temperture, Motor_Temperture, Accelator_Opening = 0, 0, 0

    pump_control_pin = 20
    led_control_pin = 21
    led_status = False

    T, A = [0,0,0,0], [0,0,0,0]
    idx = 0

    bus = Bus()

    pygame.init()
    textID = loadTexture()
    display = (800, 480)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL) #  | FULLSCREEN

    gluOrtho2D(0, 800, 0, 480)  # 2D 뷰포트 설정

    temp_lowerbound = 30
    temp_upperbound = 40

    import time
    prev_time = time.time()

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

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 왼쪽에 텍스트 표시
        draw_text_centered(f"{BUS_RoationSpeed}",230, 340, 250)
        draw_text_centered(f"RPM",520, 315, 70)  # 여기에 원하는 값을 입력해주세요.

        # 오른쪽에 사각형 표시 (백분율: 50%)
        drawAccelPercentage(10)
        draw_text_centered(f"{Accelator_Opening}%",685, 420, 100)
        #drawBatteryPercentage(30)

        scale = 0.4
        drawPicture(300, 135, 1327 * scale,515 * scale, textID)

        pygame.display.flip()
        pygame.time.wait(20)


        #펌프 컨트롤

        if temp_lowerbound > Motor_Temperture:
            GPIO.output(pump_control_pin, GPIO.LOW)

        elif temp_upperbound < Motor_Temperture:
            GPIO.output(pump_control_pin, GPIO.HIGH)

        #뒤에 등 컨트롤

        if time.time() - prev_time > 5:
            if led_status:
                GPIO.output(led_control_pin, GPIO.HIGH)
                led_status = False
            else:
                GPIO.output(led_control_pin, GPIO.LOW)
                led_status = True
            

if __name__ == "__main__":
    main()

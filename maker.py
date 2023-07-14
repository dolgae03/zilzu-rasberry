import RPi.GPIO as GPIO
import time
import requests


def changeAngletoDuty(angle):
    if angle < 0 or angle > 180:
        return None
    
    return 3 + (angle / 180) * (12.5-3)

url = 'http://192.168.0.2:8000/api/dataSend'

servo_pin_1 = 18  # 라즈베리 파이의 GPIO 핀 번호에 맞게 설정하세요.
servo_pin_2 = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin_1, GPIO.OUT)
GPIO.setup(servo_pin_2, GPIO.OUT)

pwm_1 = GPIO.PWM(servo_pin_1, 50)  # PWM 주파수를 50Hz로 설정합니다.
pwm_2 = GPIO.PWM(servo_pin_2, 50)
pwm_1.start(changeAngletoDuty(110))  #
pwm_2.start(changeAngletoDuty(180-110)) 

# pwm_1.stop(
    
# )
# pwm_2.stop()


import smbus
import math

import MPU9250

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()

SolarTrack = False
#12.5

try:

    while True:
        # 0도에서 180도까지 2초마다 움직입니다.
        imu.readSensor()
        imu.computeOrientation()

        ax, ay, az = imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2]
        a_vector = [imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2]]
        
        a = math.asin(az / (ax**2 + ay**2 + az**2) ** 0.5) * 180 / math.pi
        
        print(SolarTrack)
        if SolarTrack:
            pwm_1.ChangeDutyCycle(changeAngletoDuty(110))
            pwm_2.ChangeDutyCycle(changeAngletoDuty(70))

            print('hi')
        else:
            pwm_1.ChangeDutyCycle(changeAngletoDuty(70))
            pwm_2.ChangeDutyCycle(changeAngletoDuty(110))
            
        #-33
        data = {
            'SolarNumber': 'abcdefg',
            'Voltage': 12,
            'Charged': 3,
            'acc' : f'{int(ax)},{int(ay)},{int(az)}',
            'light' : '0,0,0,0',
            'lat': f'{int(a)}',
            'lon': '36'
        }
        
        response = requests.get(url, params=data)
        if response.json()['solar_track'] == 'False':
            SolarTrack = False
        else:
            SolarTrack = True
        time.sleep(1)

        # time.sleep(5)
    
except KeyboardInterrupt:
    pwm_1.stop()
    pwm_2.stop()

GPIO.cleanup()
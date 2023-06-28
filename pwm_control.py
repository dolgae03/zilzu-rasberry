import RPi.GPIO as GPIO
import time

BCM_num = 13

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(BCM_num, GPIO.OUT)

# for i in range(10):
#     GPIO.output(BCM_num,1)  # GPIO BCM_num번 Pin을 High(3.3V)로 만들어라
#     print('High!!!')
#     time.sleep(1)
#     GPIO.output(BCM_num,0)  # GPIO BCM_num번 Pin을 Low(0V)로 만들어라
#     print('Low~~~')
#     time.sleep(1)
# GPIO.cleanup()

# import RPi.GPIO as GPIO
# import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(BCM_num, GPIO.OUT)

p = GPIO.PWM(BCM_num, 1000)
p.start(100)
p.ChangeDutyCycle(100)
try:
    while 1:
        
except KeyboardInterrupt:
        pass
p.stop()
GPIO.cleanup()
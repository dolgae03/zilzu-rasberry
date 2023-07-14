import os
import sys
import time
import smbus
import math

import MPU9250

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()
# imu.caliberateGyro()
# imu.caliberateAccelerometer()
# or load your own caliberation file
#imu.loadCalibDataFromFile("/home/pi/calib_real_bolder.json")

while True:
    imu.readSensor()
    imu.computeOrientation()

    #print ("roll: {0} ; pitch : {1} ; yaw : {2}".format(imu.roll, imu.pitch, imu.yaw))
    print(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2])
    ax, ay, az = imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2]
    a_vector = [imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2]]
    
    a = math.asin(az / (ax**2 + ay**2 + az**2) ** 0.5) * 180 / math.pi
    b = math.acos(ax / (ax **2 + ay**2) ** 0.5) * 180 / math.pi
    c = math.acos(ay / (ax **2 + ay**2) ** 0.5) * 180 / math.pi
    
    print(a,b,c)
    
    
    time.sleep(0.1)
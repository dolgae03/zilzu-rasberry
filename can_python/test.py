import can
import os
import RPi.GPIO as GPIO
import time


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

if not os.path.isfile('./can_data_1.csv'):
    with open('can_data_1.csv', 'w') as f:
        f.write('Timestamp,BUS_Voltage(V),BUS_Current(A),BUS_Phase_Current(A),BUS_RoationSpeed(rpm)\n')

if not os.path.isfile('./can_data_2.csv'):
    with open('can_data_2.csv', 'w') as f:
        f.write('Timestamp,Controller_Teperture(C),Motor_Temperture(C),Accelator_Opening(%),STATUS,ERROR\n')

####
#the setting value is here.

write_mode = True
BCM_num = 13

####

BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed = 0, 0, 0, 0
Controller_Temperture, Motor_Temperture, Accelator_Opening = 0, 0, 0

bus = Bus()
for msg in bus:
    
    if msg.arbitration_id == 0x180117EF:
        BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed = MCU_RECIEVE_1(msg.data)
        
        if write_mode:
            with open('can_data_1.csv', 'a') as file:
                file.write("{},{},{},{},{}\n".format(msg.timestamp, BUS_Voltage, BUS_Current, BUS_Phase_Current, BUS_RoationSpeed))

    elif msg.arbitration_id == 0x180217EF:
        #Controller_Temperture, Motor_Temperture, Accelator_Opening, status, error = MCU_RECIEVE_2(msg.data)
        Controller_Temperture, Motor_Temperture, Accelator_Opening = MCU_RECIEVE_2(msg.data)

        if write_mode:        
            with open('can_data_2.csv', 'a') as f:
                #f.write("{},{},{},{},{},{}\n".format(msg.timestamp, Controller_Temperture, Motor_Temperture, Accelator_Opening, status, error))
                f.write("{},{},{},{}\n".format(msg.timestamp, Controller_Temperture, Motor_Temperture, Accelator_Opening))
                
        
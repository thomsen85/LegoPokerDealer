#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase

import socket

ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.A)
deal_motor = Motor(Port.B)
robot = DriveBase(left_motor, right_motor, 40, 100)

HOST = 'local'  # The server's hostname or IP address
PORT = 8070       # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def deal_card(times):
    print("Dealing loop")
    for _ in range(times):
        print("Dealing cards")
        deal_motor.run_angle(1000, 320) # gitte konstanter som funket for oss
        deal_motor.run_angle(-150, 200) # gitte konstanter som funket for oss

def main():
    while True:
        data = s.recv(1024)
        if data != b"":
            print(data.decode())
            if len(data.decode().split(",")) == 3:
                x, y, deal = map(int, data.decode().split(","))
                robot.drive(x,-y)    
            if deal:
                deal_card(2)         
                
if __name__=="__main__":
    main()
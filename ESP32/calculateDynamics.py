import _thread
from time import sleep
from machine import Pin, PWM, Timer, ADC

""" LIMIT SWITCH SETUP """
LS1 = Pin(4, Pin.IN, Pin.PULL_UP)
LS2 = Pin(16, Pin.IN, Pin.PULL_UP)

""" GANTRY (HORIZONTAL) MOTOR SETUP """
IN1 = Pin(25, mode=Pin.OUT)
IN2 = Pin(26, mode=Pin.OUT)
# theoretically 70 percent is optimal motor power for running long term
maxMotorPower = 99
speed_as_percent = 0
motor = PWM(IN1, freq=25000, duty_u16=0)  # clockwise is motor high rev_0
rev_motor = PWM(IN2, freq=25000)

def moveMotorRight(speed):
    motor.duty(int(0))
    rev_motor.duty(int(speed))
    
def moveMotorLeft(speed):
    motor.duty(int(speed))
    rev_motor.duty(int(0))

def calculateDynamics(pos_x,pos_x_last,t_last,checkWatchDog,x_des):
    Kp = 0.3
    if checkWatchDog == False:
        dx = pos_x - pos_x_last/t_last
        u = Kp*x_des - (Kp*pos_x + dx)
        return u
    if checkWatchDog == True:
        return
import time
from machine import Pin, PWM, Timer, ADC, PWM
# note that Rotary irq only works on the most recent micropython version and we had to update the "bootloader"? of the ESP32
from rotary_irq_esp import RotaryIRQ
import time
import socket as socket
import json
import _thread
import gc

class encoder():
    global x_pos_enc
    global lock
    def __init__(self):
        """ GANTRY (HORIZONTAL) ENCODER SETUP """
        self.pinA = Pin(39, Pin.IN)  # Set up pins for encoder
        self.pinB = Pin(36, Pin.IN)

        """ HORIZONTAL ENCODER SETUP """
        self.x_pos = 0
        self.prevA = self.pinA.value()
        self.prevB = self.pinB.value()
        self.encoder_pos = 0

        self.r = RotaryIRQ(pin_num_clk=39,
                           pin_num_dt=36,
                           min_val=0,
                           max_val=1000000,
                           reverse=False,
                           range_mode=RotaryIRQ.RANGE_WRAP)

        self.val_old = self.r.value()
        self.temp_enc_val = 0

    def readEncoder(self):
        self.temp_enc_val = self.r.value()
        
            

class actuator():
    global x_pos_enc
    global lock
    def __init__(self):
        """ LIMIT SWITCH SETUP """
        self.LS1 = Pin(4, Pin.IN, Pin.PULL_UP)
        self.LS2 = Pin(16, Pin.IN, Pin.PULL_UP)
        self.startSensor = Pin(17, Pin.IN, Pin.PULL_UP)  # not setup for hall effect
        self.endSensor = Pin(21, Pin.IN, Pin.PULL_UP)  # not setup for hall effect

        """ GANTRY (HORIZONTAL) MOTOR SETUP """
        self.IN1 = Pin(25, mode=Pin.OUT)
        self.IN2 = Pin(26, mode=Pin.OUT)
        # theoretically 70 percent is optimal motor power for running long term
        self.maxMotorPower = 99
        self.speed_as_percent = 0
        self.motor = PWM(self.IN1, freq=25000, duty_u16=0)  # clockwise is motor high rev_0
        self.rev_motor = PWM(self.IN2, freq=25000)

        """ JOYSTICK SETUP """
        self.button = Pin(15, Pin.IN, Pin.PULL_UP)
        self.xStick = ADC(Pin(34))
        self.yStick = ADC(Pin(33))
        self.xStick.atten(ADC.ATTN_11DB)  # Full range: 3.3v
        self.yStick.atten(ADC.ATTN_11DB)  # Full range: 3.3v

        # constants for running the joystick (manually calibrated)
        self.minJoy = 142
        # medJoy = 1660
        self.deadBand = 15
        self.maxJoy = 3160
        self.centerJoy = (self.maxJoy + self.minJoy) / 2
        self.slope = self.maxMotorPower / (self.maxJoy - self.centerJoy)
        # xStick.width(ADC.WIDTH_12BIT)

        """ homing flags setup"""
        self.homingSpeed = 600
        self.leftHomed = False
        self.rightHomed = False
        self.farRight = 0
        self.x_pos = 0
        self.resetZero = False

        """ Move to X setup """
        self.positioned = False
        self.tol = 1
        
        """ Auto function helper"""
        self.zeroPos = 0

    def horizontalPosition(self):
        lock.acquire()
        self.x_pos = x_pos_enc
        lock.release()
        return self.x_pos

    def getTheta(self):
        # TODO Add encoder code here!!!!
        return 13

    def checkLimLeft(self):
        if self.LS1.value() == 0:
            return True
        else:
            return False

    def checkLimRight(self):
        if self.LS2.value() == 0:
            return True
        else:
            return False

    def checkStart(self):
        if self.startSensor.value() == 0:
            return True
        else:
            return False

    def checkEnd(self):
        if self.endSensor.value() == 0:
            return True
        else:
            return False

    def checkFinished(self):
        # Helper function to check finished
        # TODO: Edit to account for debounce
        if self.checkEnd() == True:
            return True
        else:
            return False

    def moveMotorRight(self, speed):
        self.motor.duty(int(0))
        self.rev_motor.duty(int(speed))

    def moveMotorLeft(self, speed):
        self.motor.duty(int(speed))
        self.rev_motor.duty(int(0))

    def homingFunction(self):
        #print('In Homing Function')
        if self.leftHomed == False or self.resetZero == False:
            #print("Moving left")
            position = self.x_pos
            self.moveMotorLeft(self.homingSpeed)
            self.leftHomed = self.checkLimLeft()
            if self.leftHomed == True:
                self.zeroPos = self.x_pos
                self.resetZero = True
                #print('Homing Right')
            return False
        elif self.rightHomed == False and self.leftHomed == True:
            #print("Moving right")
            position = self.x_pos
            self.moveMotorRight(self.homingSpeed)
            self.rightHomed = self.checkLimRight()
            return False
        if self.rightHomed and self.leftHomed:
            #print('Done Homing')
            self.moveMotorRight(0)
            print("HERE ---------------------------------------------------------------")
            self.farRight = self.x_pos
            self.rightHomed = False
            self.leftHomed = False
            return True

    def moveToPosition(self, xcoord):
        if self.x_pos > xcoord + self.tol and not self.checkLimLeft():
            self.moveMotorLeft(self.homingSpeed)
            return False
        elif self.x_pos < xcoord - self.tol and not self.checkLimRight():
            self.moveMotorRight(self.homingSpeed)
            return False
        else:
            return True

    def manualMovement(self):
        #print("In manualmovement()")
        x_value = self.xStick.read() - self.centerJoy - 10
        y_value = self.yStick.read() - self.centerJoy - 10
        
        #Adjust due to reverse wiring of joystick
        x_value = x_value * (-1)

        speed = self.slope * x_value * 10
        buttonState = self.button.value()

        rightHit = self.checkLimRight()
        leftHit = self.checkLimLeft()

        if speed > 1023:
            speed = 1023
        if speed < -1023:
            speed = -1023

        if x_value >= self.deadBand and not rightHit:
            #print("In goingRight()")

            # run one direction
            self.motor.duty(int(0))
            self.rev_motor.duty(int(speed))
            # print("Running Right")
            # print(speed)
        elif x_value <= -self.deadBand and not leftHit:
            #print("In goingleft()")
            # run the other direction
            self.motor.duty(int(-speed))
            self.rev_motor.duty(int(0))
            # print("Running Left")
            # print(speed)
        else:
            #print("In stopped()")
            self.motor.duty(int(0))
            self.rev_motor.duty(int(0))
            # print("Stopped")

    def autoMove(self, x_des):
        return


#----------------------------------------------------------------------------------------
#End of state/actuator functions, time to multithread
# ----------------------------------------------------------------------------------------

#Changes for multithreading:
# 1) Add global lock variable to actuator and instantiate before while loop
# 2) Add global xEnc variable to actuator and instantiate before while loop
# 3) Create new encoder class with readEncoder method
# 4) Edit actuator class to remove encoder functions
# 5) Restructure while True loop


#Garbage collection function
#This was stolen straight from: https://www.youtube.com/watch?v=1q0EaTkztIs
#This functions performs a garbage collection, and then shows how much storage is in use, and how much is cfree after garbage collection
#This is helpful for debugging
def free(full=False):
    gc.collect()
    F = gc.mem_free() #Return the number of bytes of available heap RAM, or -1 if this amount is not known.
    A = gc.mem_alloc() #Return the number of bytes of heap RAM that are allocated.
    T = F + A
    P = '{0:.2f}%'.format(F / T * 100)
    if not full:
        return P
    else:
        return ('Total:{0} Free:{1} ({2})'.format(T, F, P))


def core0_thread():
    global lock
    global x_pos_enc
    myActuator = actuator()
    firstHomed = False
    while myActuator.homingFunction() == False and firstHomed == False:
        myActuator.horizontalPosition()
        print("myActuator.x_pos = " + str(myActuator.x_pos))
        if myActuator.homingFunction() == True:
            firstHomed = True
        print(myActuator.zeroPos)
        print(myActuator.farRight)
    while True:
        myActuator.horizontalPosition()
        myActuator.manualMovement()
        print("myActuator.x_pos = " + str(myActuator.x_pos))
        #Run garbage collection and print how much memory is being used
        print(free(True))
        print(myActuator.zeroPos)
        print(myActuator.farRight)


def core1_thread():
    global lock
    global x_pos_enc
    Encoder = encoder()
    while True:
        # Update Encoder.temp_enc_val to current reading from encoder
        Encoder.readEncoder()
        if not lock.acquire():
            pass
        else:
            #confirmed it is locked at this point, but not locked before
            #If we have acquired lock, we should update x_pos_enc value
            print("Second loop")
            x_pos_enc = Encoder.temp_enc_val
            lock.release()
        gc.collect() # run garbage collection to clean unused memory

#Setup global x_pos_enc value
x_pos_enc = 0

#Create lock for multithreading
lock = _thread.allocate_lock()

#Start threads:
second_thread = _thread.start_new_thread(core1_thread, ())
core0_thread()
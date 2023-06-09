import time
from machine import Pin, PWM, Timer, ADC, PWM
# note that Rotary irq only works on the most recent micropython version and we had to update the "bootloader"? of the ESP32
from rotary_irq_esp import RotaryIRQ
import time
import socket as socket
import json


class esp32():
        #iitializing variables
        def __init__(self):
            #Recieved from phone:
            self.phone_state = "select"
            self.x_des = 0
            self.y_des = 0
            self.cancel = False

            #Physical vals from actuator:
            self.x_pos = 0
            self.y_pos = 0
            self.theta = 0

            #Self updated state variables:
            self.state = "idle"
            self.finished = False
            self.homed = False

            #Instance of actuator class
            self.myActuator = actuator()


        def updatePhysicalVals(self):
            # Update variables:
            self.theta = self.myActuator.getTheta()
            self.x_pos = self.myActuator.horizontalPosition()


        def getstate(self):
            if self.phone_state == "select" and self.checkHomed() == True:
                self.state = "idle"
            elif self.phone_state == "automatic"and self.cancel==False and self.checkFinished() == False:
                self.state = "auto"
            elif self.phone_state =="manual" and self.cancel==False and self.checkFinished() == False:
                self.state = "manual"
            elif self.phone_state == "thankyou" or (self.phone_state == "automatic" and (self.cancel==True or self.checkFinished() == True)):
                self.state = "finished"
            elif self.phone_state == "thankyou" or (self.phone_state =="manual" and (self.cancel==True or self.checkFinished() == True)):
                self.state = "finished"
            elif self.phone_state == "select" and self.checkHomed() == False:
                print("error not homed")
            else:
                print ("No corresponding esp32 state")


        def actions(self):
            if self.state =="idle":
                #Do nothing
                self.myActuator.moveMotorRight(0)

            elif self.state == "auto":
                #Set homed to False:
                if self.homed == True:
                    self.homed = False
                #Auto move:
                self.myActuator.autoMove(self.x_des)

            elif self.state =="manual":
                # Set homed to False:
                if self.homed == True:
                    self.homed = False
                #Move manually:
                self.myActuator.manualMovement()

            elif self.state =="finished":
                homed = self.myActuator.homingFunction()
                if homed == True:
                    self.homed = True

        def checkFinished(self):
            #check ending sensor
            self.finished = self.myActuator.checkFinished()
            return self.finished()

        def checkHomed(self):
            return self.homed

class actuator():
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
        self.xStick = ADC(Pin(33))
        self.yStick = ADC(Pin(34))
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

        """ GANTRY (HORIZONTAL) ENCODER SETUP """
        self.pinA = Pin(39, Pin.IN)  # Set up pins for encoder
        self.pinB = Pin(36, Pin.IN)

        """ HORIZONTAL ENCODER SETUP """
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

        """ homing flags setup"""
        self.homingSpeed = 1000
        self.leftHomed = False
        self.rightHomed = False
        self.farRight = 0

        """ Move to X setup """
        self.positioned = False
        self.tol = 5

    def horizontalPosition(self):
        val_new = self.r.value()
        if self.val_old != val_new:
            self.val_old = val_new

        return val_new

    def getTheta(self):
        #TODO Add encoder code here!!!!
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
        #Helper function to check finished
        #TODO: Edit to account for debounce
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
        print('Homing Left')
        if self.leftHomed == False:
            print("Moving left")
            time.sleep_ms(50)  # TODO: delete me!!!
            position = self.horizontalPosition()
            self.moveMotorLeft(self.homingSpeed)
            self.leftHomed = self.checkLimLeft()
            # print('left homed is: ',leftHomed)
            if self.checkLimLeft():
                # print('LEFT HOMED')
                self.r.set(value=0)
                print('Homing Right')
            return False
        elif self.rightHomed == False and self.leftHomed == True:
            print("Moving right")
            time.sleep_ms(50)  # TODO: Delete me!!!
            position = self.horizontalPosition()
            # print(position)
            self.moveMotorRight(600)
            self.rightHomed = self.checkLimRight()
            # print('left homed is: ',leftHomed)
            # print('right homed is: ',rightHomed)
            # if checkLimRight():
            # print('RIGHT HOMED')
            return False
        if self.rightHomed and self.leftHomed:
            print('Done Homing')
            self.moveMotorRight(0)
            self.farRight = myActuator.horizontalPosition()
            self.rightHomed = False
            self.leftHomed = False
            return True

    def moveToPosition(self, xcoord):
        if self.horizontalPosition() > xcoord + self.tol and not self.checkLimLeft():
            self.moveMotorLeft(500)
            return False
        elif self.horizontalPosition() < xcoord - self.tol and not self.checkLimRight():
            self.moveMotorRight(600)
            return False
        else:
            return True

    def manualMovement(self):
        print("In manualmovement()")
        x_value = self.xStick.read() - self.centerJoy - 10
        y_value = self.yStick.read() - self.centerJoy - 10
        speed = self.slope * x_value * 10
        buttonState = self.button.value()

        rightHit = self.checkLimRight()
        leftHit = self.checkLimLeft()

        if speed > 1023:
            speed = 1023
        if speed < -1023:
            speed = -1023

        if x_value >= self.deadBand and not rightHit:
            print("In goingRight()")

            # run one direction
            self.motor.duty(int(0))
            self.rev_motor.duty(int(speed))
            # print("Running Right")
            # print(speed)
        elif x_value <= -self.deadBand and not leftHit:
            print("In goingleft()")
            # run the other direction
            self.motor.duty(int(-speed))
            self.rev_motor.duty(int(0))
            # print("Running Left")
            # print(speed)
        else:
            print("In stopped()")
            self.motor.duty(int(0))
            self.rev_motor.duty(int(0))
            # print("Stopped")

    def autoMove(self,x_des):
        return


## TESTING EXPLAINED
# This code will create an instance of the esp32() class, which has an actuator (myActuator) attached to it
# The ESP32 will home outside the while True loop
# The ESP32 will then continously update physical values (theta) and go into the auto section of the actions loop
# The auto section of ESP32.actions() calls myActuator.autoMove() continously

ESP32 = esp32()

#Home:
homeCheck = ESP32.myActuator.homingFunction()
while homeCheck == False:
    homeCheck = ESP32.myActuator.homingFunction()

#Set state to auto for testing:
ESP32.state = "auto"
while True:
    ESP32.updatePhysicalVals() #Not debugged yet - may give weird values
    ESP32.actions()

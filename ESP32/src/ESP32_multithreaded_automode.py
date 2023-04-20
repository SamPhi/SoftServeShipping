import time
from machine import Pin, PWM, Timer, ADC, PWM
# note that Rotary irq only works on the most recent micropython version and we had to update the "bootloader"? of the ESP32
from rotary_irq_esp import RotaryIRQ
import time
import socket as socket
import json
import _thread
import gc


class esp32():
    # iitializing variables
    def __init__(self):
        # Recieved from phone:
        self.phone_state = "select"
        self.x_des = 0
        self.y_des = 0
        self.cancel = False

        # Physical vals from actuator:
        self.x_pos = 0
        self.y_pos = 0
        self.theta = 0

        # Self updated state variables:
        self.state = "idle"
        self.finished = False
        self.homed = False
        self.partHomed = False

        # Instance of actuator class
        self.myActuator = actuator()

    def updatePhysicalVals(self):
        # Update variables:
        self.theta = self.myActuator.getTheta()
        self.x_pos = self.myActuator.horizontalPosition()
        # self.x_pos = self.myActuator.horizontalPosition()

    def getstate(self):
        if (self.phone_state == "select" or self.state == 'finished') and self.checkHomed() == True:
            self.state = "idle"
        elif self.phone_state == "automatic" and self.cancel == False and self.checkFinished() == False:
            self.state = "auto"
        elif self.phone_state == "manual" and self.cancel == False and self.checkFinished() == False:
            self.state = "manual"
        elif self.phone_state == "thankyou" or (
                self.phone_state == "automatic" and (self.cancel == True or self.checkFinished() == True)):
            self.state = "finished"
        elif self.phone_state == "thankyou" or (
                self.phone_state == "manual" and (self.cancel == True or self.checkFinished() == True)):
            self.state = "finished"
        elif self.phone_state == "select" and self.checkHomed() == False:
            print("error not homed")
        else:
            print("No corresponding esp32 state")

    def actions(self):
        if self.state == "idle":
            # Do nothing
            self.myActuator.moveMotorRight(0)
            #Reset flags
            self.finished = False

        elif self.state == "auto":
            # Set homed to False:
            if self.homed == True:
                self.homed = False
            # Auto move:
            self.myActuator.autoMove(self.x_des)

        elif self.state == "manual":
            # Set homed to False:
            if self.homed == True:
                self.homed = False
            # Move manually:
            self.myActuator.manualMovement()

        elif self.state == "finished":
            #Reset cancel flag
            if self.cancel == True:
                self.cancel = False
            if self.partHomed == False and self.homed == False:
                partHomed = self.myActuator.homingFunction()
                if partHomed == True:
                    self.partHomed = True
            else:
                print(self.getStartPos())
                moveToStart = self.myActuator.moveToPosition(self.getStartPos())
                if moveToStart == True:
                    self.homed = True
                    self.partHomed = False

    def checkFinished(self):
        # check ending sensor
        if self.finished == True:
            return True
        else:
            self.finished = self.myActuator.checkFinished()
            return self.finished

    def checkHomed(self):
        return self.homed
    
    def getStartPos(self):
        #Number decreases when moving right
        #But far left number is smaller than far right number due to wrap around
        #Find absolute difference
        rightPos = self.unWrap(self.myActuator.farRight)
        zeroPos = self.unWrap(self.myActuator.zeroPos)
        diff = abs(zeroPos - rightPos)
        startPos = self.wrap(zeroPos - int(1/16 * diff))
        return startPos
    
    #Create linear scale for measured encoder values by subtracting 999999 for numbers that have wrapped around
    #E.g. 5->5, but 999997-> -2 
    def unWrap(self,num):
        if num > 500000:
            num = num - 999999
        return num
    
    #Returns a wrapped value in the case startPos is negative
    # E.g. 127 -> 127 but -5 -> 999994
    def wrap(self,num):
        if num < 0:
            num = 999999 + num
        return num
            

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
        self.last_x_pos = 0
        self.massGantry = 1 #Kg
        self.massContainer = 0.5 #Kg
        self.lengthCable = 1 #m
        self.g = 9.81 #m/s^2
        self.dt = 0.001
        self.lastTheta = 0

        """ PID values """
        self.Kp = 0.0001
        self.Ki = 0.0001
        self.Kd = 0.0001
        
        """Angle sensor setup"""
        self.angleSensor = ADC(Pin(32)) #TODO: Change to pin in range GPIO 32-39
        self.angleSensor.atten(ADC.ATTN_11DB)

        #Empirically attained constants:
        self.center = 1863.5
        self.FortyFiveDeg = 1371.6
        self.OneDeginCounts = (self.center-self.FortyFiveDeg)/45


    def horizontalPosition(self):
        self.x_pos = x_pos_enc
        return self.x_pos

    def getTheta(self):
        ang = self.angleSensor.read()
        angDeg = (ang-self.center)/self.OneDeginCounts
        return angDeg

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
        #Fix x_Des for testing
        if x_des == 0:
            x_des = 500 #TODO: Remove me after testing!!!
        #Find theta
        theta = self.getTheta()
        #Calc errors
        theta_error = abs(self.lastTheta - theta)/self.dt
        x_error = abs(self.last_x_pos - self.x_pos)/self.dt

        #Control values
        print("Auto x_error " + str(x_error))
        print("X pos " + str(self.x_pos))


        PWM = self.Kp*x_error #TODO turn this into real value

        #Actually write calculated PWMN vals to motor
        self.writeMotors(PWM)

        #Update past values for next run
        self.last_x_pos = self.x_pos
        self.lastTheta = theta
        return

    def writeMotors(self,PWM):

        rightHit = self.checkLimRight()
        leftHit = self.checkLimLeft()

        if PWM > 1023:
            PWM = 1023
        if PWM < -1023:
            PWM = -1023

        if PWM > 0 and not rightHit: #TODO: Check if directions correct
            # run one direction
            self.motor.duty(int(0))
            self.rev_motor.duty(int(PWM))
            # print("Running Right")
            # print(speed)
        elif PWM <0 and not leftHit: #TODO: Check if directions correct
            # print("In goingleft()")
            # run the other direction
            self.motor.duty(int(-PWM))
            self.rev_motor.duty(int(0))
            # print("Running Left")
            # print(speed)
        else:
            # print("In stopped()")
            self.motor.duty(int(0))
            self.rev_motor.duty(int(0))
            # print("Stopped")





def phone_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('SoftServeShipping', 'SoftServeShipping')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('192.168.43.1', 12345)  # Should be '192.168.43.1', 12345
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)
    return sock


# communicaiton Functions
def recieveDate(sock, ESP32):  # Receive data
    data = sock.recv(1024)
    # if no new data, return (hence values stay same as before
    if not data:
        return
    # If recieved multiple data packets since last check, return
    if "}{" in data.decode():
        return
    data = json.loads(data.decode())
    ESP32.x_des = data.get("x_des")
    ESP32.y_des = data.get("y_des")
    ESP32.phone_state = data.get("state")
    ESP32.cancel = data.get("cancel")


def send_data(sock, x_pos, y_pos, homed, finished, theta):
    # Send data
    positionalDataArr = json.dumps(
        {"x_pos": x_pos, "y_pos": y_pos, "homed": homed, "finished": finished, "theta": theta})
    message = positionalDataArr.encode()
    # print('sending {!r}'.format(message))
    sock.sendall(message)

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
    phone_connect()
    sock = start_server()
    ESP32 = esp32()
    ESP32.getstate()
    ESP32.state = "manual"
    global lock
    global x_pos_enc
    while True:
        recieveDate(sock, ESP32)
        print("ESP32 state is: " + str(ESP32.state))
        print("phone_state is: " + str(ESP32.phone_state))
        print(ESP32.myActuator.x_pos)
        #This calls ESP32.updatePhysicalVals which calls myActuator.horizontalPositon() which acquires and releases lock
        #We do this because we want to call lock only when strictly necessary, i.e. when we read the encoder
        lock.acquire()
        ESP32.updatePhysicalVals()
        lock.release()
        ESP32.getstate()
        ESP32.actions()
        send_data(sock, ESP32.x_pos, ESP32.y_pos, ESP32.homed, ESP32.finished, ESP32.theta)
        #Run garbage collection and print how much memory is being used
        print(free(True))
        print("Esp32 checkHomed(): " + str(ESP32.checkHomed()))
        print("Esp32 cancel: " + str(ESP32.cancel))
        print("Esp32 checkFinished: " + str(ESP32.checkFinished()))



def core1_thread():
    global lock
    global x_pos_enc
    Encoder = encoder()
    while True:
        # Update Encoder.temp_enc_val to current reading from encoder
        Encoder.readEncoder()
        if not lock.acquire(0):
            pass
        else:
            #If we have acquired lock, we should update x_pos_enc value
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
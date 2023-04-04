from machine import Pin, PWM, Timer, ADC, PWM
# note that Rotary irq only works on the most recent micropython version and we had to update the "bootloader"? of the ESP32
from rotary_irq_esp import RotaryIRQ
import time


""" LIMIT SWITCH SETUP """
LS1 = Pin(4, Pin.IN, Pin.PULL_UP)
LS2 = Pin(16, Pin.IN, Pin.PULL_UP)
startSensor = Pin(17, Pin.IN, Pin.PULL_UP) # not setup for hall effect
endSensor = Pin(21, Pin.IN, Pin.PULL_UP)# not setup for hall effect


""" GANTRY (HORIZONTAL) MOTOR SETUP """
IN1 = Pin(25, mode=Pin.OUT)
IN2 = Pin(26, mode=Pin.OUT)
# theoretically 70 percent is optimal motor power for running long term
maxMotorPower = 99
speed_as_percent = 0
motor = PWM(IN1, freq=25000, duty_u16=0)  # clockwise is motor high rev_0
rev_motor = PWM(IN2, freq=25000)

""" JOYSTICK SETUP """
button = Pin(15, Pin.IN, Pin.PULL_UP)
xStick = ADC(Pin(33))
yStick = ADC(Pin(34))
xStick.atten(ADC.ATTN_11DB)  # Full range: 3.3v
yStick.atten(ADC.ATTN_11DB)  # Full range: 3.3v

# constants for running the joystick (manually calibrated)
minJoy = 142
# medJoy = 1660
deadBand = 15
maxJoy = 3160
centerJoy = (maxJoy+minJoy)/2
slope = maxMotorPower/(maxJoy - centerJoy)
# xStick.width(ADC.WIDTH_12BIT)

""" GANTRY (HORIZONTAL) ENCODER SETUP """
pinA = Pin(39, Pin.IN)  # Set up pins for encoder
pinB = Pin(36, Pin.IN)

""" HORIZONTAL ENCODER SETUP """
prevA = pinA.value()
prevB = pinB.value()
encoder_pos = 0

r = RotaryIRQ(pin_num_clk=39,
              pin_num_dt=36,
              min_val=0,
              max_val=1000000,
              reverse=False,
              range_mode=RotaryIRQ.RANGE_WRAP)

val_old = r.value()

time.sleep_ms(50)


""" FUNCTIONS """

def horizontalPosition(val_old):
    val_new = r.value()
    if val_old != val_new:
        val_old = val_new
        
    return val_new

def checkLimLeft():
    if LS1.value() == 0:
        return True
    else:
        return False
    
def checkLimRight():
    if LS2.value() == 0:
        return True
    else:
        return False
    
def checkStart():
    if startSensor.value() == 0:
        return True
    else:
        return False
    
def checkEnd():
    if endSensor.value() == 0:
        return True
    else:
        return False
    
    
def moveMotorRight(speed):
    motor.duty(int(0))
    rev_motor.duty(int(speed))
    
def moveMotorLeft(speed):
    motor.duty(int(speed))
    rev_motor.duty(int(0))

homed = False

def homingFunction():
    homingSpeed = 500
    leftHomed = False
    rightHomed = False
    print('Homing Left')
    while not leftHomed:
        time.sleep_ms(50)
        position = horizontalPosition(val_old)
        moveMotorLeft(homingSpeed)
        leftHomed = checkLimLeft()
        #print('left homed is: ',leftHomed)
        if checkLimLeft():
            #print('LEFT HOMED')
            r.set(value=0)
            print('Homing Right')
    while not rightHomed:
        time.sleep_ms(50)
        position = horizontalPosition(val_old)
        #print(position)
        moveMotorRight(600)
        rightHomed = checkLimRight()
        #print('left homed is: ',leftHomed)
        #print('right homed is: ',rightHomed)
        #if checkLimRight():
            #print('RIGHT HOMED')
    if rightHomed and leftHomed:
        print('Done Homing')
        return True
    
def moveToPosition(xcoord):
    positioned = False
    tol = 5
    while not positioned:
        if horizontalPosition(val_old) > xcoord + tol and not checkLimLeft():
            moveMotorLeft(500)
        elif horizontalPosition(val_old) < xcoord - tol and not checkLimRight():
            moveMotorRight(600)
        else:
            positioned = True
    return True

def manualMovement():
    x_value = xStick.read() - centerJoy - 10
    y_value = yStick.read() - centerJoy - 10
    speed = slope*x_value*10
    buttonState = button.value()
    
    rightHit = checkLimRight()
    leftHit = checkLimLeft()

    if speed > 1023:
        speed = 1023
    if speed < -1023:
        speed = -1023

    if x_value >= deadBand and not rightHit:
        # run one direction
        motor.duty(int(0))
        rev_motor.duty(int(speed))
        # print("Running Right")
        # print(speed)
    elif x_value <= -deadBand and not leftHit:
        # run the other direction
        motor.duty(int(-speed))
        rev_motor.duty(int(0))
        # print("Running Left")
        # print(speed)
    else:
        motor.duty(int(0))
        rev_motor.duty(int(0))
        # print("Stopped")

def checkWatchDog(): #take in 2x1 vector of states, return T if hit
    if LS1 or LS2 == True:
        return True
    else:
        return False

def calculateDynamics(pos_x,pos_x_last,t_last,x_des):
    Kp = 0.3
    dx = pos_x - pos_x_last/t_last
    u = Kp*x_des - (Kp*pos_x + dx)
    return u

def writeMotors(PWM_x):
    if checkWatchDog() == False:
        if PWM_x < 0:
                moveMotorRight(abs(PWM_x)*1000) #assuming ~1000 is max PWM
        elif PWM_x > 0:
            moveMotorRight(abs(PWM_x)*1000) #assuming ~1000 is max PWM
        else:
            return
    return

""" RUNNING LOOP """

while True:
    position = horizontalPosition(val_old)
    # print('Position = ', position)
    
    # homing sequence + move to start
    homed = True # cop out to avoid homing at start *for debugging)
    if not homed:
        homed = homingFunction()
        farRight = horizontalPosition(val_old)
        print('Far Right position is',farRight)
        print('Moving to start')
        moveToPosition(int(farRight*.125))
        print('Successfully moved to start!!!')
    
    looptime = 50
    time.sleep_ms(looptime)
    # time.sleep_us(100)

    
    writeMotors(calculateDynamics(position,val_old,looptime/1000,0))

    if checkStart():
        print('Start sensor TRIGGERED')
    else:
        print('Start sensor NOT triggered')

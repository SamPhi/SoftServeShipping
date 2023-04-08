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

""" FUNCTIONS """

def horizontalPosition(val_old):
    val_new = r.value()
    if val_old != val_new:
        val_old = val_new
        print('result =', val_new)    
        
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
    
    
def moveMotorLeft(speed):
    motor.duty(int(0))
    rev_motor.duty(int(speed))
    #print('right')
    
def moveMotorRight(speed):
    motor.duty(int(speed))
    rev_motor.duty(int(0))
    #print('left')

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

def checkWatchDog(): #take in 2x1 vector of states, return F if hit
    #print('ls1', bool(LS1.value()), 'ls2', bool(LS2.value()))
    if (LS1.value() == False) or (LS2.value() == False):
        #print('wd false')
        return False
    else:
        #print('wd true')
        return True
def calculateDynamics(pos_x,pos_x_last,t_last,x_des):
    Kp = 0.001
    dx = pos_x - pos_x_last/t_last
    u = Kp*(x_des - pos_x)
    print('u = ', u)
    return u

def writeMotors(PWM_x):
    #print('wd = ', checkWatchDog())
    if checkWatchDog() == True:
        if PWM_x < 0:
            moveMotorRight(min(abs(PWM_x)*1000,1023)) #assuming ~1000 is max PWM
            print(PWM_x, ' right')
        elif PWM_x > 0:
            moveMotorLeft(min(abs(PWM_x)*1000, 1023)) #assuming ~1000 is max PWM
            print(PWM_x, ' left')
        else:
            return
    return

""" RUNNING LOOP """
r.set(value=0)
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
    
    time.sleep_ms(50)
    # time.sleep_us(100)
    
    moveMotorLeft(500)
    #manualMovement() # currently controls horizontal movement, NOT Y MOVEMENT *yet
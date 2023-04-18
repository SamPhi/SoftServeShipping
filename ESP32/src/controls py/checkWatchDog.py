from machine import Pin, PWM, Timer, ADC, PWM

LS1 = Pin(4, Pin.IN, Pin.PULL_UP)
LS2 = Pin(16, Pin.IN, Pin.PULL_UP)

def checkWatchDog(switchState): #take in 4x1 vector of states, return T if hit
    if switchState == True:
        return True
    else:
        return False
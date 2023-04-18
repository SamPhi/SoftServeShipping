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
        """ homing flags setup"""
        self.x_pos = 0


    def horizontalPosition(self):
        lock.acquire()
        self.x_pos = x_pos_enc
        lock.release()
        return self.x_pos


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
    while True:
        myActuator.horizontalPosition()
        time.sleep(0.1)
        print("myActuator.x_pos = " + str(myActuator.x_pos))
        #Run garbage collection and print how much memory is being used
        print(free(True))



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
            #TODO: May need to add lock.acquire here, not sure if 'if not lock.acquire' does it automatically
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























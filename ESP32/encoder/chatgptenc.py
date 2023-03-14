from machine import Pin
from time import sleep_us

# Set up pins for encoder
pinA = Pin(14, Pin.IN)
pinB = Pin(32, Pin.IN)

# Initialize variables for tracking encoder state
prevA = pinA.value()
prevB = pinB.value()
encoder_pos = 0

# Define the interrupt handler function
def encoder_handler(pin):
    global prevA, prevB, encoder_pos
    currA = pinA.value()
    currB = pinB.value()
    if currA != prevA:
        if currA != currB:
            encoder_pos += 1
        else:
            encoder_pos -= 1
    else:
        if currA == currB:
            encoder_pos += 1
        else:
            encoder_pos -= 1
    prevA, prevB = currA, currB

# Set up the interrupt on the A pin
pinA.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_handler)

# Main loop
while True:
    print("Encoder position:", encoder_pos)
    sleep_us(100)

from machine import Pin
from time import sleep_us

# Set up pins for encoder
pinA = Pin(14, Pin.IN)
pinB = Pin(32, Pin.IN)

# Initialize variables for tracking encoder state
prevA = pinA.value()
prevB = pinB.value()
encoder_pos = 0

# Main loop
while True:
    # Poll the encoder state
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

    # Print the encoder position
    print("Encoder position:", encoder_pos)

    # Wait a short time to avoid busy-waiting
    sleep_us(100)

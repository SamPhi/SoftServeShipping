from machine import Pin

LED = pin(2, Pin.OUT)

while True:
    LED.high()
    delay(1000)
    LED.low()
    
    
    
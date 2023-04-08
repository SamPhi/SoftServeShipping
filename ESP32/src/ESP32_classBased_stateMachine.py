#from machine import Pin, PWM, Timer, ADC, PWM
#from rotary_irq_esp import RotaryIRQ
import socket as socket
import json
import time

#def homingFunction()
#moveToPosition(startingPosition)??Where to put move to starting point ??


#lastState & newState??
#manualMovement

class esp32():
        #iitializing variables
        def __init__(self):
            self.state = "idle"
            self.x_pos = 0
            self.y_pos = 0
            self.finished = False
            self.homed = False
            self.theta = 0
            self.cancel = False
            self.x_des =0
            self.y_des = 0
            self.phone_state = "selector"


        def getstate(self):
            if self.phone_state == "selector" and self.checkHomed() == True:
                self.state = "idle"
            elif self.phone_state == "auto"and self.cancel==False and self.checkFinished() == False:
                self.state = "auto"
            elif self.phone_state =="manual" and self.cancel==False and self.checkFinished() == False:
                self.state = "manual"
            elif self.phone_state == "auto"and (self.cancel==True or self.checkFinished() == True):
                self.state = "auto"
            elif self.phone_state =="manual" and (self.cancel==True or self.checkFinished() == True):
                self.state = "manual"
            elif self.phone_state == "selector" and self.checkHomed() == False:
                print("error not homed")
            else:
                print ("No corresponding esp32 state")


        def actions(self):
            if self.state =="idle":
                PWM_x = 0
                #motor.duty(PWM_x)
                #if homingFunction() == False: #error_homed_state, to be removed
                #    print("error_not_homed")

            elif self.state == "auto":
                return #comment me out
                #PWM_x = caluclate_pwm_x(des_x, pos_x)
                #writeMotors(PWM_x, checkWatchDpg(LS3, LS4))

            elif self.state =="manual":
                manualMovement()

            elif self.state =="finished":
                A = 2 #dummy to avoid indentation error



        def checkFinished(self):
            #check ending sensor
            return False

        def checkHomed(self):
            return False


def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('127.0.0.1', 12345) #Should be '192.168.43.1', 12345
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)
    return sock

#communicaiton Functions
def recieveDate(sock, ESP32):# Receive data
    data = sock.recv(1024)
    #if no new data, return (hence values stay same as befor
    if not data:
        return
        #If recieved multiple data packets since last check, only take the most recent
        if len(data) != 56:
            data = data[-56:]
        data = json.loads(data.decode())
        ESP32.x_des = data.get("x_des")
        ESP32.y_des = data.get("y_des")
        ESP32.phone_state = data.get("state")
        ESP32.cancel = data.get("cancel")


def send_data(sock, x_pos,y_pos,homed,finished,theta):
    # Send data
    positionalDataArr = json.dumps({"x_pos": x_pos, "y_pos": y_pos, "homed": homed, "finished": finished, "theta": theta})
    message = positionalDataArr.encode()
    #print('sending {!r}'.format(message))
    sock.sendall(message)


# Motor Control Functions

def manualMovement():
    return #comment me out
    # x_value = xStick.read() - centerJoy - 10
    # y_value = yStick.read() - centerJoy - 10
    # speed = slope*x_value*10
    # buttonState = button.value()
    #
    # rightHit = checkLimRight()
    # leftHit = checkLimLeft()
    #
    # if speed > 1023:
    #     speed = 1023
    # if speed < -1023:
    #     speed = -1023
    #
    # if x_value >= deadBand and not rightHit:
    #     # run one direction
    #     motor.duty(int(0))
    #     rev_motor.duty(int(speed))
    #     # print("Running Right")
    #     # print(speed)
    # elif x_value <= -deadBand and not leftHit:
    #     # run the other direction
    #     motor.duty(int(-speed))
    #     rev_motor.duty(int(0))
    #     # print("Running Left")
    #     # print(speed)
    # else:
    #     motor.duty(int(0))
    #     rev_motor.duty(int(0))
    #     # print("Stopped")



sock = start_server()
ESP32 = esp32()
ESP32.getstate()


while True:
    recieveDate(sock, ESP32)
    print("ESP32 state is: " + str(ESP32.state))
    print("phone_state is: " + str(ESP32.phone_state))
    ESP32.getstate()
    ESP32.actions()
    send_data(sock, ESP32.x_pos, ESP32.y_pos, ESP32.homed, ESP32.finished, ESP32.theta)

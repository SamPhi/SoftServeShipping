import time
import math
import json, socket


class gamePlayer():
    def __init__(self):

        # initialize state variables
        self.cancel = False
        self.x_des = 0  # Desired x position - set default to target location for actual thing
        self.y_des = 0  # desired y position - set default to target location for actual thing
        self.lastRunTime = 0  # time for previous run
        self.maxTheta = 0  # max theta variable
        self.state = "select"
        self.newState = "select"
        self.x_pos = 0
        self.y_pos = 0
        self.homed = True
        self.finished = False
        self.theta = 0


    def getState()
        #some logic that decides what the state should be
        self.state = "name_of_state"

    def doStateActions()
        if state == idle:
            #do idle things
        if state == other
            #do othger things

    # helper function to update value of thetaMax
    def updateMaxTheta(self):
        if self.theta > self.maxTheta:
            self.maxTheta = self.theta
        return

    # helper function for change conditions/actions of state machine
    def stateChanged(self, newState):
        if newState == "manual":
            self.runTimer.startTimer()
        elif newState == "automatic":
            self.runTimer.startTimer()
        elif newState == "thankyou":
            self.lastRunTime = self.runTimer.getTimeString()
            self.runTimer.resetTimer()
        elif newState == "select":
            # do nothing I guess?
            A = 1  # This state is superfluous rn but will have functionality later so stupid fix to indentation block expected error
        else:
            print("error in changeState: newState!= a valid state name")

    def updateStateNonButton(self,newState):
        #updates for the three non-button cases as per the state machine diagram
        if newState == "manual" and self.finished == True:
            return "thankyou"
        if newState == "automatic" and self.finished == True:
            return "thankyou"
        if newState == "thankyou" and self.homed == True:
            return "select"




def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific address and port
    server_address = ('192.168.43.1', 12345)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)
    # Wait for a connection
    #print('waiting for a connection')
    connection, client_address = sock.accept()
    return connection

def send_data(sock, x_des, y_des, state, cancel):
    # Send data
    phoneDataArr = json.dumps({"x_des": x_des, "y_des": y_des, "state": state, "cancel": cancel})
    message = phoneDataArr.encode()
    #print('sending {!r}'.format(message))
    sock.sendall(message)

def receive_data(sock,game):
    # Receive data
    data = sock.recv(1024)
    if not data:
        return
    # If recieved multiple data packets since last check, only take the most recent
    if len(data) != 75:
        data = data[-75:]
    data = json.loads(data.decode())
    game.x_pos = data.get("x_pos")
    game.y_pos = data.get("y_pos")
    game.homed = data.get("homed")
    game.finished = data.get("finished")
    game.theta = data.get("theta")


if __name__ == "__main__":
    #Start an instance of gamePlayer() class
    game = gamePlayer()
    #start our server for ESP32 comms
    sock = start_server()
    while True:
        newState = game.newState
        game.updater(newState)
        game.update()
        send_data(sock, game.x_des, game.y_des, game.state, game.cancel)
        receive_data(sock, game)
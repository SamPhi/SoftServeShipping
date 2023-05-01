import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import time
import math
import json, socket
import numpy as np
import gamePlayer
import select_frame
import manual_frame
import thankyou_frame
import swingAnimation
import scoresTable
import timer


def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific address and port
    server_address = ('127.0.0.1', 12345) #Should be:'192.168.43.1', 12345 for phone, '1
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
    ##sock.sendall("\n".encode())

def receive_data(sock,game):
    # Receive data
    data = sock.recv(1024)
    if not data:
        return
    # If recieved multiple data packets since last check, return
    if "}{" in data.decode():
        return
    data = json.loads(data.decode())
    game.x_pos = data.get("x_pos")
    game.y_pos = data.get("y_pos")
    game.homed = data.get("homed")
    game.finished = data.get("finished")
    game.theta = data.get("theta")


if __name__ == "__main__":
    #Start an instance of gamePlayer() class
    game = gamePlayer.gamePlayer()
    #start our server for ESP32 comms
    sock = start_server()
    while True:
        game.actions()
        game.getState()
        game.update()
        print("last state = " + game.lastState)
        #print("Starting send data")
        print("current state = " + game.state)
        send_data(sock, game.x_des, game.y_des, game.state, game.cancel)
        #print("Finished send data")
        #print("Starting recieveing ESP32 data")
        receive_data(sock, game)
        #print("Finished recieveing ESP32 data. Recieved message:")
        #print(game.x_des, game.y_des, game.state, game.cancel)
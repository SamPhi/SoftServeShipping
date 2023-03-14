import sys
import socket
import getopt
import threading
import subprocess

target = '192.168.43.1'
port = 8888

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target,port))
while True:
	data = client.recv(4096)
	if not data:
		break
	print(data)
	


import sys
import socket
import getopt
import threading
import subprocess

target = '192.168.43.1'
port = 8888

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((target, port))
server.listen(5)

while True:
	client_socket, address = server.accept()
#	client_thread = threading.Thread(
#	    target=client_handler,
#	    args=(client_socket,)
#	)
#client_thread.start()

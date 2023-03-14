# echo-server.py

import socket

HOST = "192.168.43.1"  # Standard loopback interface address (localhost is 0.0.0.0)
PORT = 8888  # Port to listen on (non-privileged ports are > 1023)

#mySocket = socket.socket()
#mySocket.bind((HOST,PORT))
#print(socket.gethostname())

#mySocket.listen(1)
#conn,addr = mySocket.accept()
#print("connection from: " + str(addr))
#while True:
#    data = conn.recv(1024).decode()
#    print("from connected user: " + str(data))
#    data = str(data).upper()
#    print("sending: " + str(data))
#    conn.send(data.encode())
#conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
     s.bind((HOST, PORT))
     s.listen()
     conn, addr = s.accept()
     with conn:
         print(f"Connected by {addr}")
         while True:
             data = conn.recv(1024)
             if not data:
                 break
             conn.sendall(data)

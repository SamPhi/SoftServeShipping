import socket

# Set up the connection
host = '192.168.43.1'  # This should be the IP address of your phone's hotspot
port = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

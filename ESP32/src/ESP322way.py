import socket

def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('192.168.43.1', 12345)
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)
    return sock

def send_data(sock, data):
    # Send data
    message = data.encode()
    print('sending {!r}'.format(message))
    sock.sendall(message)

def receive_data(sock):
    # Receive data
    data = sock.recv(1024)
    print('received {!r}'.format(data.decode()))

if __name__ == '__main__':
    sock = start_server()
    while True:
        data = "test"
        send_data(sock, data)
        receive_data(sock)

import socket, json

x_des = 10
y_des = 23
state = "Test state"
cancel = False


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

def receive_data(sock):
    # Receive data
    data = sock.recv(1024)
    data = json.loads(data.decode())
    x_pos = data.get("x_pos")
    y_pos = data.get("y_pos")
    homed = data.get("homed")
    finished = data.get("finished")
    theta = data.get("theta")
    phoneData = [x_pos, y_pos, homed, finished, theta]
    return phoneData


if __name__ == '__main__':
    sock = start_server()
    while True:
        phoneData = receive_data(sock)
        print("Message recieved:")
        print(phoneData)
        send_data(sock, x_des, y_des, state, cancel)
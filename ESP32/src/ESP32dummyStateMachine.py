import socket, json,time

x_pos = 50
y_pos = 1000
homed = True
finished = False
theta = 12
positionalData = [x_pos,y_pos,homed,finished,theta]

def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('127.0.0.1', 12345) #Should be '192.168.43.1', 12345
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)
    return sock

def send_data(sock, x_pos,y_pos,homed,finished,theta):
    # Send data
    positionalDataArr = json.dumps({"x_pos": x_pos, "y_pos": y_pos, "homed": homed, "finished": finished, "theta": theta})
    message = positionalDataArr.encode()
    #print('sending {!r}'.format(message))
    sock.sendall(message)

def receive_data(sock):
    # Receive data
    data = sock.recv(1024)
    #if no new data, return (hence values stay same as before
    if not data:
        return
    #If recieved multiple data packets since last check, return
    if "}{" in data.decode():
        return
    data = json.loads(data.decode())
    x_des = data.get("x_des")
    y_des = data.get("y_des")
    state = data.get("state")
    cancel = data.get("cancel")
    phoneData = [x_des,y_des,state,cancel]
    return phoneData

if __name__ == '__main__':
    sock = start_server()
    while True:
        theta += 1
        finished = False #input("Input Finished:")
        homed = False #input("input homed")
        send_data(sock, x_pos,y_pos,homed,finished,theta)
        time.sleep(0.001)
        phoneData = receive_data(sock)
        print(phoneData)
        time.sleep(0.001)
        
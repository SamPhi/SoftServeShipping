import socket, json, time


#Initialize real variables (to be carried over to final script)
host = '192.168.43.1'  # This should be the IP address of your phone's hotspot
port = 12345

#Initialize dummy variables (to be reasigned in final script)
pos_x = 50
pos_y = 1000
LS1 = True
LS2 = False
theta = 12
positionalData = [pos_x,pos_y,LS1,LS2,theta]


#start_server function begins connection to phone. To be called once on startup
def start_server():
	global client_socket #Must define as global to be accessible in other functions
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((host, port))

#write_Phone function sends data to laptop. To be called multiple times during operation
def write_Phone(positioanlData):
	#global client_socket #must define as global to be accessible in other functions
	#positionalDataArr = json.dumps({"pos_x": pos_x, "pos_y":pos_y,"LS1":LS1,"LS2":LS2,"theta":theta}) #uses Json to create dictionary that can be read by phone at other end
    positionalDataArr = input("Go:")
    client_socket.send(positionalDataArr.encode())
    #client_socket.close() #closes connection - to be deleted?

def read_Phone():
    #global client_socket
    data = client_socket.recv(1024)
    #data = json.loads(data.decode())
    data = data.decode()
    #x_des = data.get("x_des")
    #y_des = data.get("y_des")
    #state = data.get("state")
    #cancel = data.get("cancel")
    #print(x_des, y_des, state, cancel)
    print(data)
    return
	
	
#def phone_connect():
#    sta_if = network.WLAN(network.STA_IF)
#    if not sta_if.isconnected():
#        print('connecting to network...')
#        sta_if.active(True)
#        sta_if.connect('SoftServeShipping', 'SoftServeShipping')
#        while not sta_if.isconnected():
#            pass
#    print('network config:', sta_if.ifconfig())
    


#Calls functions for testing purposes
print('Hello')
#phone_connect()
start_server()
while True:
    print('Start write from Phone')
    write_Phone(positionalData)
    print('Done write from Phone')
    #time.sleep(2)
    print('Start read from Phone')
    read_Phone()
    print('Done read from Phone')
    #time.sleep(2)
 #   print('Start Write on phone')
 #   write_Phone(positionalData)
 #   print('Done Write on phone')
 #   time.sleep(2)

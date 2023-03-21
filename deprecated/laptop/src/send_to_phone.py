import socket, json

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
	global client_socket #must define as global to be accessible in other functions
	positionalDataArr = json.dumps({"pos_x": pos_x, "pos_y":pos_y,"LS1":LS1,"LS2":LS2,"theta":theta}) #uses Json to create dictionary that can be read by phone at other end
	client_socket.send(positionalDataArr.encode()) #sends data
	client_socket.close() #closes connection - to be deleted?

#Calls functions for testing purposes
start_server()
write_Phone(positionalData)
write_Phone(positionalData)
write_Phone(positionalData)


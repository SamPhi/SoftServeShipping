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

def start_server():
	global client_socket
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((host, port))


def write_Phone(positioanlData):
	global client_socket
	positionalDataArr = json.dumps({"pos_x": pos_x, "pos_y":pos_y,"LS1":LS1,"LS2":LS2,"theta":theta})
	#for s in positionalDataArr:
	client_socket.send(positionalDataArr.encode())
		#client_socket.sendall(repr(s).encode('utf-8'))
#			print("Ran")
	# Close the connection
	client_socket.close()

start_server()
write_Phone(positionalData)
#Add global clientsocket

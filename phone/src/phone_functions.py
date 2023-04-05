import socket,json

#Initialize Variables (to be copied to final script)
host = ''
port = 12345

#Function startServer begins server for laptop communication
def startServer():
	global connection
	global address
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((host,port))
	server_socket.listen(1) #Listen for one incoming connection

	#Accept a connection from laptop
	connection,address = server_socket.accept()
        

#Function  readLaptop readspositional data from laptop
def readLaptop():
        global connection 
        global address
        data = connection.recv(1024)
        if not data:
                return
        data = json.loads(data.decode())
        pos_x = data.get("pos_x")
        pos_y = data.get("pos_y")
        LS1 = data.get("LS1")
        LS2 = data.get("LS2")
        theta = data.get("theta")
        print(pos_x,pos_y,LS1,LS2,theta)

startServer()
while True:
	readLaptop()
#connection.close()

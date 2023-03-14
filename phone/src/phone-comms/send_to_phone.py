import socket

# Send some strings
strings = ['Hello', 'World', 'Python']
for s in strings:
    client_socket.sendall(s.encode())

# Close the connection
client_socket.close()


# import socket for client tcp connection
import socket

# default host and port for the client to connect to
HOST = 'localhost'
PORT = 12345

# client will use this host and port to connect to a running server

# returns a connected socket used by main.py for client mode
def connect_client(host=HOST, port=PORT):
# create a tcp socket and connect to the server address
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((host, port))
    print(f"Connected to {host}:{port}")
    return client_sock

# call connect_client() from main.py when client mode is selected

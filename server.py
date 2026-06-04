# import socket for server network communication
import socket

# default host and port for the server to listen on
HOST = 'localhost'
PORT = 12345

# server binds to this host and port before accepting a client

# returns the client connection and address once a client connects
def start_server(host=HOST, port=PORT):
# create a tcp server socket and accept one incoming connection
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    print(f"Server listening on {host}:{port}...")
    conn, addr = server_sock.accept()
    print(f"Connected by {addr}")
    return conn, addr

# call start_server() from main.py when server mode is selected

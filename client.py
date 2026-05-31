import socket

HOST = 'localhost'
PORT = 12345

def connect_client(host=HOST, port=PORT):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((host, port))
    print(f"Connected to {host}:{port}")
    return client_sock

# Call connect_client() from main.py when client mode is selected.

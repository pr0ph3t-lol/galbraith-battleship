import socket

HOST = 'localhost'
PORT = 12345

def start_server(host=HOST, port=PORT):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    print(f"Server listening on {host}:{port}...")
    conn, addr = server_sock.accept()
    print(f"Connected by {addr}")
    return conn, addr

# Call start_server() from main.py when server mode is selected.

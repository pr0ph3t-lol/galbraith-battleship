import socket

HOST = 'localhost'
PORT = 12345

socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_conn.connect((HOST, PORT))

print(f"Connected to {HOST}:{PORT}")

# Now use 'socket_conn' to send/receive data
# Example: socket_conn.send(b"data"), socket_conn.recv(1024)

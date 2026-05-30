import socket

HOST = 'localhost'
PORT = 12345

socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_conn.bind((HOST, PORT))
socket_conn.listen(1)

print(f"Server listening on {HOST}:{PORT}...")
conn, addr = socket_conn.accept()
print(f"Connected by {addr}")

# Now use 'conn' to send/receive data
# Example: conn.send(b"data"), conn.recv(1024)

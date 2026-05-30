import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))

server.listen(1)

while True:
    print("Waiting for a connection...")
    conn, addr = server.accept()
    conn.send("Welcome to the server!".encode())

    data = conn.recv(1024).decode()
    print(f"Recievved from {addr}: {data}")

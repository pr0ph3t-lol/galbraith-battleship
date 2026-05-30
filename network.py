import socket
while True:
    user_port = int(input("Enter port number to connect to: "))
    if 1024 <= user_port <= 65535:
        break


HOST = '127.0.0.1'  # localhost
PORT = 65432        # any free port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print("Waiting for connection...")
    conn, addr = server.accept()
    with conn:
        print("Connected by", addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print("Received:", data.decode())
            conn.sendall(b"ACK")
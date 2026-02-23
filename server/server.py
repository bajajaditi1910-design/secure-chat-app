import socket
import threading

HOST = '127.0.0.1'   # localhost
PORT = 5000          # port number

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

print(f"[SERVER] Running on {HOST}:{PORT}")

def handle_client(client):
    while True:
        try:
            message = client.recv(4096)
            if not message:
                break
            broadcast(message, client)
        except:
            break

    clients.remove(client)
    client.close()

def broadcast(message, sender):
    for client in clients:
        if client != sender:
            client.send(message)

def receive_connections():
    while True:
        client, address = server.accept()
        print(f"[CONNECTED] {address}")
        clients.append(client)

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

receive_connections()
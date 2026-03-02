import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []

print(f"[SERVER] Running on {HOST}:{PORT}")

def broadcast(message, sender):
    for client in clients:
        if client != sender:
            try:
                client.send(message)
            except:
                client.close()
                if client in clients:
                    clients.remove(client)

def handle_client(client):
    while True:
        try:
            message = client.recv(4096)
            if not message:
                break
            broadcast(message, client)
        except:
            break

    if client in clients:
        clients.remove(client)
    client.close()
    print("[DISCONNECTED] Client removed")

def accept_connections():
    while True:
        client, addr = server.accept()
        print(f"[CONNECTED] {addr}")
        clients.append(client)

        # Send READY whenever 2 or more clients exist
        if len(clients) >= 2:
            print("[SERVER] Sending READY to all clients.")
            for c in clients:
                try:
                    c.send(b"READY")
                except:
                    pass

        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

accept_connections()
import socket
import threading
from flask import Flask

# ==============================
# Flask Setup (Serve Frontend)
# ==============================

app = Flask(__name__, static_folder="../static")

@app.route("/")
def serve_index():
    return app.send_static_file("index.html")


# ==============================
# Blind Relay Chat Server
# ==============================

HOST = "127.0.0.1"
PORT = 5000

clients = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"[SERVER] Running on {HOST}:{PORT}")


def broadcast(sender, data: bytes):
    """
    Forward encrypted bytes to other clients.
    Server does NOT inspect or decrypt.
    """
    for client in clients:
        if client != sender:
            try:
                client.sendall(data)
            except:
                client.close()
                if client in clients:
                    clients.remove(client)


def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            broadcast(client_socket, data)
        except:
            break

    client_socket.close()
    if client_socket in clients:
        clients.remove(client_socket)
    print("[DISCONNECTED] Client removed")


def accept_connections():
    while True:
        client_socket, addr = server_socket.accept()
        clients.append(client_socket)
        print(f"[CONNECTED] {addr}")

        if len(clients) >= 2:
            print("[SERVER] Sending READY to all clients")
            for c in clients:
                try:
                    c.sendall(b"READY")
                except:
                    pass

        threading.Thread(
            target=handle_client,
            args=(client_socket,),
            daemon=True
        ).start()


# ==============================
# Run Everything
# ==============================

if __name__ == "__main__":
    # Start socket server in background
    threading.Thread(target=accept_connections, daemon=True).start()

    # Start Flask app
    app.run(debug=True)
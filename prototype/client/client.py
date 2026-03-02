import socket
import threading
import os
import hmac

from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

role = input("Enter role (1 = initiator, 2 = responder): ")

# ---------- WAIT FOR READY (TCP-SAFE) ----------
print("[INFO] Waiting for READY from server...")
buffer = b""

while True:
    data = client.recv(4096)
    buffer += data
    if b"READY" in buffer:
        buffer = buffer.replace(b"READY", b"")
        print("[INFO] Both clients connected. Starting secure handshake.")
        break

print("[SECURE] Performing Diffie-Hellman key exchange...")

# ---------- FIXED DH PARAMETERS ----------
p = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF",
    16
)

g = 2
parameters = dh.DHParameterNumbers(p, g).parameters(default_backend())
private_key = parameters.generate_private_key()
public_key = private_key.public_key()

public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# ---------- ORDERED KEY EXCHANGE ----------
if role == "1":
    client.send(public_bytes)
    peer_public_bytes = client.recv(4096)
else:
    if buffer:
        peer_public_bytes = buffer
    else:
        peer_public_bytes = client.recv(4096)
    client.send(public_bytes)

peer_public_key = serialization.load_pem_public_key(
    peer_public_bytes,
    backend=default_backend()
)

shared_secret = private_key.exchange(peer_public_key)
print("[SECURE] Shared secret established")

# ---------- DERIVE AES + HMAC KEYS ----------
digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
digest.update(shared_secret)
master_key = digest.finalize()

aes_key = master_key[:16]      # AES-128
hmac_key = master_key[16:]     # HMAC-SHA256

print("[SECURE] AES key derived")
print("[SECURE] HMAC key derived")

# ---------- ENCRYPT ----------
def encrypt_message(msg):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded = padder.update(msg.encode()) + padder.finalize()

    ciphertext = encryptor.update(padded) + encryptor.finalize()
    mac = hmac.new(hmac_key, iv + ciphertext, digestmod="sha256").digest()

    return iv + ciphertext + mac

# ---------- DECRYPT ----------
def decrypt_message(data):
    iv = data[:16]
    mac_received = data[-32:]
    ciphertext = data[16:-32]

    mac_calculated = hmac.new(hmac_key, iv + ciphertext, digestmod="sha256").digest()

    if not hmac.compare_digest(mac_received, mac_calculated):
        return "[WARNING] Message integrity compromised!"

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()

    return plaintext.decode()

# ---------- CHAT ----------
def receive_messages():
    while True:
        try:
            data = client.recv(4096)
            print("Peer:", decrypt_message(data))
        except:
            break

def send_messages():
    while True:
        msg = input()
        client.send(encrypt_message(msg))

threading.Thread(target=receive_messages, daemon=True).start()
send_messages()
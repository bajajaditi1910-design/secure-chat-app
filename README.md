# Secure Chat Application 🔐

A dual-layered secure messaging system featuring military-grade end-to-end encryption (E2EE). This project demonstrates the evolution from a **Python CLI Prototype** to a **Modern Web Application**.

## 🚀 The Development Journey
This project was built in two distinct phases:
1.  **Phase 1: The Prototype (Demo Chat)** - A terminal-based version to prove the Diffie-Hellman and AES encryption logic.
2.  **Phase 2: The Web App** - A full-stack implementation with a polished UI, using a Python WebSocket relay and a responsive frontend.

---

## 🛠 Features
* **Diffie-Hellman Key Exchange:** Securely generates shared secret keys over insecure channels.
* **AES-256 Encryption:** All messages are encrypted/decrypted locally on the client-side.
* **Zero-Trust Relay:** The server acts as a "blind" messenger—it cannot read your chats.
* **HMAC Integrity:** Ensures messages haven't been tampered with during transit.
* **Live Identity:** Unique device-based session management.

---

## 📂 Project Structure
```text
SECURE-CHAT-APP/
├── backend/             # Live Web App Server logic
│   ├── crypto_utils.py  # Shared encryption functions
│   ├── server.py        # WebSocket relay server
│   └── ws_bridge.py     # Connection handling
├── frontend/            # Web User Interface
│   ├── index.html       # Secure Chat UI
│   ├── styles.css       # Modern Cyberpunk theme
│   └── script.js        # Frontend logic & E2EE implementation
├── prototype/           # The "Demo Chat" (CLI version)
│   ├── client/client.py # Terminal-based client
│   └── server/server.py # Original socket server
└── screenshots/         # Visual proof of handshake & encryption
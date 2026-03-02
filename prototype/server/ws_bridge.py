#!/usr/bin/env python3
"""
WebSocket Bridge for SecureChat
Bridges WebSocket clients (browser) to TCP Socket Server (Python backend)
"""

import asyncio
import websockets
import socket
import json
import threading
from datetime import datetime
from crypto_utils import CryptoManager

# Configuration
WS_HOST = '0.0.0.0'
WS_PORT = 8000
TCP_HOST = '127.0.0.1'
TCP_PORT = 5000

# Store WebSocket clients
ws_clients = {}
# Store TCP socket connections
tcp_connections = {}
# Store crypto managers per client
crypto_managers = {}


class TCPBridge:
    """Bridges a WebSocket client to the TCP server"""
    
    def __init__(self, client_id, websocket):
        self.client_id = client_id
        self.websocket = websocket
        self.tcp_socket = None
        self.crypto = CryptoManager()
        self.running = False
        
    async def connect_to_tcp(self):
        """Connect to the TCP server"""
        try:
            loop = asyncio.get_event_loop()
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Connect to TCP server in non-blocking way
            await loop.run_in_executor(None, self.tcp_socket.connect, (TCP_HOST, TCP_PORT))
            
            print(f"[{datetime.now()}] Client {self.client_id} connected to TCP server")
            self.running = True
            
            # Start listening to TCP messages
            asyncio.create_task(self.tcp_listener())
            
            return True
        except Exception as e:
            print(f"[{datetime.now()}] TCP connection failed: {e}")
            return False
    
    async def tcp_listener(self):
        """Listen for messages from TCP server and forward to WebSocket"""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Receive from TCP server
                data = await loop.run_in_executor(None, self.tcp_socket.recv, 4096)
                
                if not data:
                    break
                
                # Check if it's READY signal
                if data == b"READY":
                    await self.send_to_websocket({
                        'type': 'system',
                        'message': 'Both clients connected - Ready for handshake'
                    })
                    continue
                
                # Check if it's a public key (PEM format)
                if b'BEGIN PUBLIC KEY' in data:
                    # Store peer's public key
                    peer_public_key = data.decode('utf-8')
                    self.crypto.set_peer_public_key(peer_public_key)
                    
                    # Compute shared secret
                    shared_secret = self.crypto.compute_shared_secret()
                    
                    await self.send_to_websocket({
                        'type': 'public_key',
                        'data': {
                            'publicKey': peer_public_key,
                            'sharedSecret': shared_secret[:32] + '...'  # Partial for display
                        }
                    })
                    continue
                
                # Otherwise it's an encrypted message
                try:
                    # Decrypt the message
                    plaintext = self.crypto.decrypt_message(data)
                    
                    await self.send_to_websocket({
                        'type': 'message',
                        'sender': 'peer',
                        'text': plaintext,
                        'encrypted': data.hex()[:48] + '...',
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    })
                except Exception as e:
                    print(f"[{datetime.now()}] Decryption error: {e}")
                    
            except Exception as e:
                print(f"[{datetime.now()}] TCP listener error: {e}")
                break
        
        print(f"[{datetime.now()}] TCP listener stopped for {self.client_id}")
    
    async def send_to_tcp(self, data):
        """Send data to TCP server"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.tcp_socket.send, data)
        except Exception as e:
            print(f"[{datetime.now()}] TCP send error: {e}")
    
    async def send_to_websocket(self, message):
        """Send message to WebSocket client"""
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            print(f"[{datetime.now()}] WebSocket send error: {e}")
    
    def disconnect(self):
        """Disconnect from TCP server"""
        self.running = False
        if self.tcp_socket:
            try:
                self.tcp_socket.close()
            except:
                pass


async def handle_websocket(websocket, path):
    """Handle WebSocket connections"""
    client_id = None
    bridge = None
    
    try:
        print(f"[{datetime.now()}] New WebSocket connection from {websocket.remote_address}")
        
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'handshake':
                    # Initialize client
                    client_id = data['data']['clientId']
                    client_public_key = data['data']['publicKey']
                    
                    print(f"[{datetime.now()}] Handshake from {client_id}")
                    
                    # Create bridge to TCP server
                    bridge = TCPBridge(client_id, websocket)
                    ws_clients[client_id] = bridge
                    
                    # Generate crypto keys
                    bridge.crypto.generate_keys()
                    
                    # Connect to TCP server
                    if await bridge.connect_to_tcp():
                        # Send our public key to TCP server
                        our_public_key = bridge.crypto.get_public_key_pem()
                        await bridge.send_to_tcp(our_public_key.encode('utf-8'))
                        
                        # Send confirmation to WebSocket
                        await bridge.send_to_websocket({
                            'type': 'handshake_ack',
                            'message': 'Connected to server'
                        })
                    else:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': 'Failed to connect to TCP server'
                        }))
                
                elif msg_type == 'message':
                    # Encrypt and send message
                    if bridge and bridge.running:
                        plaintext = data['data']['text']
                        
                        # Encrypt the message
                        encrypted_data = bridge.crypto.encrypt_message(plaintext)
                        
                        # Send to TCP server
                        await bridge.send_to_tcp(encrypted_data)
                        
                        print(f"[{datetime.now()}] Relayed encrypted message from {client_id}")
                
                elif msg_type == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
                    
            except json.JSONDecodeError:
                print(f"[{datetime.now()}] Invalid JSON received")
            except Exception as e:
                print(f"[{datetime.now()}] Message handling error: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"[{datetime.now()}] WebSocket connection closed")
    finally:
        # Cleanup
        if client_id and client_id in ws_clients:
            del ws_clients[client_id]
        if bridge:
            bridge.disconnect()


async def main():
    """Start the WebSocket bridge server"""
    print("=" * 70)
    print("SecureChat WebSocket Bridge")
    print("=" * 70)
    print(f"WebSocket Server: ws://{WS_HOST}:{WS_PORT}")
    print(f"TCP Server: {TCP_HOST}:{TCP_PORT}")
    print(f"Time: {datetime.now()}")
    print("=" * 70)
    print("\n⚠️  Make sure the TCP server (chat-server.py) is running on port 5000")
    print("\nWaiting for connections...\n")
    
    async with websockets.serve(handle_websocket, WS_HOST, WS_PORT):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBridge server stopped by user")
    except Exception as e:
        print(f"\n\nBridge server error: {e}")

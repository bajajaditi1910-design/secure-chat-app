#!/usr/bin/env python3
"""
WebSocket Bridge for SecureChat
Bridges WebSocket clients (browser) to TCP Socket Server (Python backend)
Updated for Cloud Deployment (Render/Railway)
"""

import asyncio
import websockets
import socket
import json
import os
from datetime import datetime
from backend.crypto_utils import CryptoManager

# Configuration - Updated for Render compatibility
WS_HOST = '0.0.0.0'
# Render provides a port via the PORT environment variable
WS_PORT = int(os.environ.get("PORT", 8000))

# For the 'Sidecar' method, TCP server runs on the same instance
TCP_HOST = '127.0.0.1'
TCP_PORT = 5000

# Store WebSocket clients
ws_clients = {}

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
                    peer_public_key = data.decode('utf-8')
                    self.crypto.set_peer_public_key(peer_public_key)
                    shared_secret = self.crypto.compute_shared_secret()
                    
                    await self.send_to_websocket({
                        'type': 'public_key',
                        'data': {
                            'publicKey': peer_public_key,
                            'sharedSecret': shared_secret[:32] + '...' 
                        }
                    })
                    continue
                
                # Decrypt message
                try:
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
                    client_id = data['data']['clientId']
                    bridge = TCPBridge(client_id, websocket)
                    ws_clients[client_id] = bridge
                    
                    bridge.crypto.generate_keys()
                    
                    if await bridge.connect_to_tcp():
                        our_public_key = bridge.crypto.get_public_key_pem()
                        await bridge.send_to_tcp(our_public_key.encode('utf-8'))
                        
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
                    if bridge and bridge.running:
                        plaintext = data['data']['text']
                        encrypted_data = bridge.crypto.encrypt_message(plaintext)
                        await bridge.send_to_tcp(encrypted_data)
                
                elif msg_type == 'ping':
                    await websocket.send(json.dumps({'type': 'pong'}))
                    
            except json.JSONDecodeError:
                print(f"[{datetime.now()}] Invalid JSON received")
            except Exception as e:
                print(f"[{datetime.now()}] Message handling error: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"[{datetime.now()}] WebSocket connection closed")
    finally:
        if client_id in ws_clients:
            del ws_clients[client_id]
        if bridge:
            bridge.disconnect()

async def main():
    """Start the WebSocket bridge server"""
    print("=" * 70)
    print("SecureChat WebSocket Bridge - PRODUCTION READY")
    print("=" * 70)
    print(f"WebSocket Server: 0.0.0.0:{WS_PORT}")
    print(f"TCP Target: {TCP_HOST}:{TCP_PORT}")
    print("=" * 70)
    
    async with websockets.serve(handle_websocket, WS_HOST, WS_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBridge server stopped")
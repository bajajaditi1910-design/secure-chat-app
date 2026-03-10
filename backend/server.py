import asyncio
import websockets
import json

# Keep track of all connected clients
clients = set()

async def handler(websocket):
    print("[CONNECTED] New client")
    clients.add(websocket)

    try:
        async for message in websocket:
            # IMPORTANT:
            # message is already encrypted JSON from client
            # server NEVER decrypts

            print("[RELAY] Encrypted message forwarded")

            # Broadcast encrypted message to everyone else
            for client in clients:
                if client != websocket:
                    await client.send(message)

    except websockets.exceptions.ConnectionClosed:
        print("[DISCONNECTED] Client left")

    finally:
        clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("🔐 Secure WebSocket Backend running on port 8000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
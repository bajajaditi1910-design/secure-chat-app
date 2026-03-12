import asyncio
import websockets
import json

# Tracks current active connections: {websocket_object: "username"}
active_clients = {}

async def broadcast_user_list():
    """Update all clients with the current online users."""
    if not active_clients:
        return
    usernames = list(active_clients.values())
    message = json.dumps({"type": "user_list", "users": usernames})
    for ws in list(active_clients.keys()):
        try:
            await ws.send(message)
        except:
            pass

async def handler(websocket):
    print("[CONNECTED] New connection")
    try:
        async for message in websocket:
            data = json.loads(message)

            # --- Persistent Identity Logic ---
            if data.get("type") == "login":
                username = data.get("username")
                
                # Check if this name is already active on ANOTHER device
                if username in active_clients.values():
                    await websocket.send(json.dumps({
                        "type": "login_error",
                        "message": "This username is already active on another device."
                    }))
                else:
                    active_clients[websocket] = username
                    await websocket.send(json.dumps({
                        "type": "login_success",
                        "username": username
                    }))
                    await broadcast_user_list()

            # --- Zero-Trust Relay (AES/HMAC Data) ---
            elif data.get("type") == "chat":
                # Blindly forward encrypted payload to others
                for ws in active_clients:
                    if ws != websocket:
                        await ws.send(json.dumps(data))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if websocket in active_clients:
            print(f"[DISCONNECTED] {active_clients[websocket]} left")
            del active_clients[websocket]
        await broadcast_user_list()

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("🔐 Backend Relay Running on Port 8000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
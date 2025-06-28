# ---------------------------------------------------------------
# File        : frontend.py
# Author      : Shivam Garg
# Created on  : 27-06-2005

# Copyright (c) Shivam Garg. All rights reserved.
# ---------------------------------------------------------------

import asyncio
import websockets
import json
from typing import Set

# Store connected frontend clients
frontend_clients: Set[websockets.WebSocketServerProtocol] = set()

async def frontend_handler(websocket, path):
    """Handle frontend WebSocket connections."""
    frontend_clients.add(websocket)
    print(f"[+] Frontend client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            # Handle messages from frontend clients if needed
            print(f"[FRONTEND] Received: {message}")
            # Echo back or process as needed
            await websocket.send(f"Echo: {message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"[-] Frontend client disconnected: {websocket.remote_address}")
    finally:
        frontend_clients.discard(websocket)

async def relay_to_frontend(message: str):
    """Relay message to all connected frontend clients."""
    if not frontend_clients:
        return
    
    # Create a copy of the set to avoid modification during iteration
    clients_copy = frontend_clients.copy()
    
    # Send to all connected clients
    disconnected_clients = []
    for client in clients_copy:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            disconnected_clients.append(client)
        except Exception as e:
            print(f"[ERROR] Failed to send to frontend client: {e}")
            disconnected_clients.append(client)
    
    # Remove disconnected clients
    for client in disconnected_clients:
        frontend_clients.discard(client)

async def broadcast_to_frontend(data: dict):
    """Broadcast structured data to frontend clients."""
    message = json.dumps(data)
    await relay_to_frontend(message)

def get_frontend_client_count() -> int:
    """Get the number of connected frontend clients."""
    return len(frontend_clients)

async def close_all_frontend_connections():
    """Close all frontend connections gracefully."""
    if not frontend_clients:
        return
    
    print(f"[+] Closing {len(frontend_clients)} frontend connections...")
    
    # Create a copy to avoid modification during iteration
    clients_copy = frontend_clients.copy()
    
    # Close all connections
    for client in clients_copy:
        try:
            await client.close()
        except Exception as e:
            print(f"[ERROR] Failed to close frontend client: {e}")
    
    # Clear the set
    frontend_clients.clear()
    print("[+] All frontend connections closed.")
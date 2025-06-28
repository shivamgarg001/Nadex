# ---------------------------------------------------------------
# File        : main.py
# Author      : Shivam Garg
# Created on  : 27-06-2005

# Copyright (c) Shivam Garg. All rights reserved.
# ---------------------------------------------------------------

import asyncio
import signal
import sys
import websockets
import contextlib

from .config import Config
from .helpers import get_session_info, fetch_market_tree, extract_forex_ids, map_market_data, print_market_mapping
from .websocket_manager import WebSocketManager
from .frontend import frontend_handler, close_all_frontend_connections

# Global shutdown event
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\n[!] Received signal {signum}. Initiating graceful shutdown...")
    shutdown_event.set()

async def main():
    """Main application entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 1) Start frontend server
    server = await websockets.serve(frontend_handler, "0.0.0.0", Config.FRONTEND_PORT)
    print(f"[+] Frontend WS listening on ws://0.0.0.0:{Config.FRONTEND_PORT}")

    try:
        # 2) Get session info and market data
        sid, host, phase = get_session_info()
        print(f"[+] Session={sid} phase={phase+2} host={host}")

        tree = fetch_market_tree()
        fx_ids = extract_forex_ids(tree)
        if not fx_ids:
            print("[-] No forex IDs found, exiting.")
            return

        mapping = map_market_data(fx_ids)
        print_market_mapping(mapping)

        # 3) Start WebSocket manager
        mgr = WebSocketManager(sid, phase, host, mapping, fx_ids, shutdown_event)
        nadex_task = asyncio.create_task(mgr.listen_and_relay())

        # 4) Wait for shutdown signal
        await shutdown_event.wait()
        print("\n[!] Shutdown requested — cleaning up…")

        # 5) Cancel WebSocket manager
        nadex_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await nadex_task

    except Exception as e:
        print(f"[ERROR] {e}")
        raise
    finally:
        # 6) Close all connections
        await close_all_frontend_connections()
        server.close()
        await server.wait_closed()
        print("[+] All done. Bye.")

def cli_entry():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    else:
        sys.exit(0)
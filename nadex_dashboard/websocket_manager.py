import asyncio
import datetime
import time
import websockets
from collections import defaultdict

from config import Config
from messages import WebSocketMessages, MessageTable
from parsing import update_table_mapping, clear_table_mapping, process_message
from frontend import relay_to_frontend
from helpers import fetch_market_tree, extract_forex_ids, map_market_data

class WebSocketManager:
    """Manages WebSocket connections and subscriptions to Nadex."""
    
    def __init__(self, session_id, phase, host, market_mapping, forex_ids, shutdown_event):
        self.session = session_id
        self.phase = phase + 2
        self.host = host
        self.mapping = market_mapping
        self.fx_ids = forex_ids
        self.shutdown_event = shutdown_event

        self.table_counter = Config.INITIAL_TABLE_COUNTER
        self.req_phase_counter = Config.INITIAL_REQ_PHASE_COUNTER
        self.win_phase = Config.WIN_PHASE

        self.last_ping = time.time()
        self.ping_interval = Config.PING_INTERVAL

        self.message_table = MessageTable()

    async def send_initial_subscriptions(self, ws):
        """Send initial subscription messages."""
        print("[+] Sending initial subscriptions…")
        self.message_table.clear()
        
        # bind_session
        msg = WebSocketMessages.get_bind_session_message(self.session, self.phase)
        await ws.send(msg)
        self.message_table.add_message("BIND", 1, "Session bind")
        await asyncio.sleep(0.1)

        # core (2–7)
        core = WebSocketMessages.get_core_subscriptions(self.session, Config.NADEX_USER_ID)
        for i, m in enumerate(core, start=2):
            await ws.send(m)
            self.message_table.add_message("CORE", i, f"Core idx {i}")
            await asyncio.sleep(0.1)

        # binary FX (8–14)
        bins = WebSocketMessages.get_binary_fx_subscriptions(self.session)
        for idx, m in enumerate(bins, start=8):
            await ws.send(m)
            self.message_table.add_message("BINARY", idx, f"Bin idx {idx}")
            await asyncio.sleep(0.1)

        print(f"[+] Done init (1–14)")

    async def send_strike_subscriptions(self, ws):
        """Send strike subscription messages."""
        print(f"[+] Starting strike subs at table {self.table_counter}")
        count = 0
        for mid, ueps in self.mapping.items():
            for ue, eps in ueps.items():
                for epic in eps:
                    if self.shutdown_event.is_set():
                        return
                    
                    update_table_mapping(epic, self.table_counter, "STRIKE")
                    
                    enc = epic.replace(".", "%2E").replace("-", "%2D")
                    m1 = WebSocketMessages.get_strike_message_type1(
                        self.session, enc, self.table_counter, self.req_phase_counter, self.win_phase
                    )
                    await ws.send(m1)
                    self.message_table.add_message("STRIKE1", self.table_counter, epic)
                    self.table_counter += 1
                    self.req_phase_counter += 1
                    await asyncio.sleep(0.05)
                    
                    update_table_mapping(epic, self.table_counter, "ORDERBOOK")
                    m2 = WebSocketMessages.get_strike_message_type2(
                        self.session, enc, self.table_counter, self.req_phase_counter, self.win_phase
                    )
                    await ws.send(m2)
                    self.message_table.add_message("STRIKE2", self.table_counter, epic)
                    self.table_counter += 1
                    self.req_phase_counter += 1
                    await asyncio.sleep(0.05)
                    count += 1
        print(f"[+] Sent {count} strike subs")

    async def send_hierarchy_subscriptions(self, ws):
        """Send hierarchy subscription messages."""
        print(f"[+] Starting hierarchy subs at table {self.table_counter}")
        for fid in self.fx_ids:
            if self.shutdown_event.is_set():
                return
            m = WebSocketMessages.get_hierarchy_message(
                self.session, fid, self.table_counter, self.req_phase_counter, self.win_phase
            )
            await ws.send(m)
            self.message_table.add_message("HIER", self.table_counter, fid)
            self.table_counter += 1
            self.req_phase_counter += 1
            await asyncio.sleep(0.1)
        print(f"[+] Sent {len(self.fx_ids)} hierarchy subs")

    async def handle_ping_pong(self, ws):
        """Handle ping/pong messages to keep connection alive."""
        while not self.shutdown_event.is_set():
            if time.time() - self.last_ping >= self.ping_interval:
                ping = WebSocketMessages.get_ping_message(self.session, self.phase)
                await ws.send(ping)
                self.last_ping = time.time()
                print(f"[PING] @ {time.strftime('%H:%M:%S')}")
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=1.0)
                break
            except asyncio.TimeoutError:
                continue

    async def resubscribe_instruments(self, ws):
        """Periodically resubscribe to instruments."""
        while not self.shutdown_event.is_set():
            now = datetime.datetime.now()
            # next 5-min mark
            nxt = ((now.minute // 5) + 1) * 5
            if nxt >= 60:
                nxt_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
            else:
                nxt_time = now.replace(minute=nxt, second=0, microsecond=0)
            wait = (nxt_time - now).total_seconds()
            print(f"[TIMER] wait {int(wait)}s until {nxt_time.strftime('%H:%M:%S')}")
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=wait)
                break
            except asyncio.TimeoutError:
                pass
            if self.shutdown_event.is_set():
                break

            print(f"[RESUB] @ {datetime.datetime.now().strftime('%H:%M:%S')}")
            tree = fetch_market_tree()
            fx_ids = extract_forex_ids(tree)
            if not fx_ids:
                print("[-] none found on resub")
                continue
            self.mapping = map_market_data(fx_ids)
            clear_table_mapping()  # Clear old mappings
            await self.send_strike_subscriptions(ws)

    async def listen_and_relay(self):
        """Main WebSocket listener that relays messages."""
        uri = f"wss://{self.host}/lightstreamer"
        async with websockets.connect(uri, subprotocols=["js.lightstreamer.com"]) as nadex_ws:
            await self.send_initial_subscriptions(nadex_ws)
            self.message_table.print_table()

            await self.send_strike_subscriptions(nadex_ws)
            await self.send_hierarchy_subscriptions(nadex_ws)
            self.message_table.print_table()

            # Start background tasks
            ping_task = asyncio.create_task(self.handle_ping_pong(nadex_ws))
            resub_task = asyncio.create_task(self.resubscribe_instruments(nadex_ws))

            print("[+] Relaying Nadex → Frontends…")
            async for msg in nadex_ws:
                if self.shutdown_event.is_set():
                    break
                    
                # Detect PONG
                if "PONG" in msg.upper():
                    print(f"[PONG] @ {time.strftime('%H:%M:%S')}")
                    
                # Relay to frontend and process message
                await relay_to_frontend(msg)
                process_message(msg)

            # Clean up background tasks
            ping_task.cancel()
            resub_task.cancel()
            try:
                await ping_task
                await resub_task
            except asyncio.CancelledError:
                pass
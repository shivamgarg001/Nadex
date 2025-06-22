import asyncio
import json
import websockets
import requests
import re
import time
from collections import defaultdict

xst_token = None

def get_xst_token():
    global xst_token

    url = "https://demo-trade.nadex.com/iDeal/v2/security/authenticate"
    headers = {
        "Accept": "application/json; charset=UTF-8",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://platform.nadex.com",
        "User-Agent": "Mozilla/5.0",
        "x-device-user-agent": "vendor=IG | applicationType=Nadex | platform=web | deviceType=phone | version=0.907.0+78b9f706"
    }
    payload = {
        "username": "demo-shivam001",  
        "password": "cBj2AfSSAX4NBXc"  
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    token = response.headers.get("x-security-token")
    if not token:
        raise Exception("x-security-token not found in response headers")
    
    print(f"Obtained xst token: {token}")
    xst_token = token
    return token

def get_session_info():
    get_xst_token()

    url = "https://demo-upd.nadex.com/lightstreamer/create_session.js"
    payload = {
        "LS_phase": "2301",
        "LS_cause": "new.api",
        "LS_polling": "true",
        "LS_polling_millis": "0",
        "LS_idle_millis": "0",
        "LS_client_version": "6.1",
        "LS_adapter_set": "InVisionProvider",
        "LS_user": "SHIVAM001",
        "LS_password": f"XST-{xst_token}",
        "LS_container": "lsc"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://platform.nadex.com",
        "Referer": "https://platform.nadex.com/",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.post(url, data=payload, headers=headers)
    body = response.text

    # Extract session, host, and phase from the JS response
    session_match = re.search(r"start\('([^']+)',", body)
    addr_match = re.search(r"start\('[^']+',\s*'([^']+)'", body)
    phase_match = re.search(r"setPhase\((\d+)\);", body)

    if session_match and addr_match and phase_match:
        return {
            "session_id": session_match.group(1),
            "phase": phase_match.group(1),
            "host": addr_match.group(1)
        }
    else:
        raise Exception("Failed to extract session info from create_session.js")

def fetch_market_tree():
    if not xst_token:
        raise Exception("xst_token is not available")

    url = "https://demo-trade.nadex.com/iDeal/markets/hierarchy/tree/full"
    headers = {
        ":authority": "demo-trade.nadex.com",
        ":method": "GET",
        ":path": "/iDeal/markets/hierarchy/tree/full",
        ":scheme": "https",
        "accept": "application/json; charset=UTF-8",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8",
        "authorization": "Bearer undefined",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://platform.nadex.com",
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "x-device-user-agent": "vendor=IG | applicationType=Nadex | platform=web | deviceType=phone | version=0.907.0+78b9f706",
        "x-security-token": xst_token
    }

    filtered_headers = {k: v for k, v in headers.items() if not k.startswith(":")}

    response = requests.get(url, headers=filtered_headers)
    response.raise_for_status()
    data = response.json()
    print(f"[+] Market Tree Response Status: {response.status_code}")
    return data

def extract_forex_ids(tree):
    """Find the '5 Minute Binaries' → 'Forex' children IDs."""
    for node in tree.get("topLevelNodes", []):
        if node.get("name", "").lower() == "5 minute binaries":
            for child in node.get("children", []):
                if child.get("name", "").lower() == "forex":
                    return [c["id"] for c in child.get("children", [])]
    return []

def fetch_navigation_by_id(market_id):
    """Call the navigation endpoint for a given market ID."""
    url = f"https://demo-trade.nadex.com/iDeal/markets/navigation/{market_id}"
    headers = {
        "accept": "application/json; charset=UTF-8",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://platform.nadex.com",
        "referer": "https://platform.nadex.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "x-device-user-agent": "vendor=IG | applicationType=Nadex | platform=web | deviceType=phone | version=0.907.0+78b9f706",
        "x-security-token": xst_token
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def map_market_data(forex_ids):
    """
    Create mapping: id -> underlyingEpic -> [list of epics]
    """
    market_mapping = defaultdict(lambda: defaultdict(list))
    
    for market_id in forex_ids:
        print(f"\n=== Processing market ID {market_id} ===")
        try:
            nav_data = fetch_navigation_by_id(market_id)
            
            # Extract markets from the response
            markets = nav_data.get("markets", [])
            
            for market in markets:
                epic = market.get("epic", "")
                underlying_epic = market.get("underlyingEpic", "")
                
                if epic and underlying_epic:
                    market_mapping[market_id][underlying_epic].append(epic)
            
            print(f"Found {len(markets)} markets for ID {market_id}")
            
        except Exception as e:
            print(f"Error fetching navigation for market ID {market_id}: {e}")
    
    return market_mapping

class WebSocketManager:
    def __init__(self, session_id, phase, host):
        self.session_id = session_id
        self.phase = int(phase)
        self.host = host
        self.table_counter = 15  # Start after the initial 7 forex subscriptions (tables 8-14)
        self.req_phase_counter = 663  # Start from 663 as shown in your example
        self.win_phase = 63  # Fixed window phase
        
    async def send_initial_subscriptions(self, ws):
        """Send bind session and core subscriptions (Tables 1-14)"""
        # Bind session (Table 1)
        bind_session = (
            "bind_session\r\n"
            f"LS_session={self.session_id}&LS_phase={self.phase}&LS_cause=loop1&LS_container=lsc&control\r\n"
            f"LS_mode=RAW&LS_id=M___.HB%7CHB.U.HEARTBEAT.IP&LS_schema=HEARTBEAT&"
            f"LS_requested_max_frequency=1&LS_table=1&LS_req_phase=619&LS_win_phase=50&LS_op=add&LS_session={self.session_id}&"
        )

        # Core Subscriptions (Tables 2-7)
        core_subs = [
            f"control\r\nLS_mode=RAW&LS_id=V2-M-MESSAGE_EVENT_HANDLER%7CSHIVAM001&LS_schema=message&"
            f"LS_requested_max_frequency=1&LS_table=2&LS_req_phase=620&LS_win_phase=50&LS_op=add&LS_session={self.session_id}&",

            f"control\r\nLS_mode=MERGE&LS_id=V2-AD-AC_AVAILABLE_BALANCE%2CAC_USED_MARGIN%7CACC.SHIVAM001&"
            f"LS_schema=AC_AVAILABLE_BALANCE%20AC_USED_MARGIN&LS_snapshot=true&LS_requested_max_frequency=1&"
            f"LS_table=3&LS_req_phase=621&LS_win_phase=50&LS_op=add&LS_session={self.session_id}&",

            f"control\r\nLS_mode=RAW&LS_id=V2-M-MESSAGE_EVENT_HANDLER%7CSHIVAM001-OP-JSON&LS_schema=json&"
            f"LS_requested_max_frequency=1&LS_table=4&LS_req_phase=622&LS_win_phase=50&LS_op=add&LS_session={self.session_id}&",

            f"control\r\nLS_mode=RAW&LS_id=M___.MGE%7CSHIVAM001-LGT&LS_schema=message&"
            f"LS_requested_max_frequency=1&LS_table=5&LS_req_phase=623&LS_win_phase=50&LS_op=add&LS_session={self.session_id}&",

            f"control\r\nLS_mode=RAW&LS_id=V2-M-MESSAGE_EVENT_HANDLER%7CSHIVAM001-WO-JSON&LS_schema=json&"
            f"LS_requested_max_frequency=1&LS_table=6&LS_req_phase=624&LS_win_phase=50&LS_op=add&LS_session={self.session_id}&",

            f"control\r\nLS_mode=RAW&LS_id=V2-M-MESSAGE_EVENT_HANDLER%7CSHIVAM001-OH-JSON&LS_schema=json&"
            f"LS_requested_max_frequency=1&LS_table=7&LS_req_phase=625&LS_win_phase=50&LS_op=add&LS_session={self.session_id}&"
        ]

        # Binary FX Pairs Subscriptions (Tables 8–14)
        pairs = [
            ("8", "SAUDUSD"),
            ("9", "SEURUSD"),
            ("10", "SGBPUSD"),
            ("11", "SUSDJPY"),
            ("12", "SEURJPY"),
            ("13", "SGBPJPY"),
            ("14", "SUSDCAD"),
        ]

        binary_subs = []
        for table, sym in pairs:
            phase_val = str(625 + int(table))
            msg = (
                "control\r\n"
                f"LS_mode=MERGE&LS_id=V2-F-LTP%2CUTM%7CCH.U.X%3A{sym}:1321%3ABLD.OPT-1-1.IP&"
                "LS_schema=lastTradedPrice%20updateTime&LS_snapshot=true&LS_requested_max_frequency=1&"
                f"LS_table={table}&LS_req_phase={phase_val}&LS_win_phase=50&LS_op=add&LS_session={self.session_id}&"
            )
            binary_subs.append(msg)

        # Send all initial messages
        all_msgs = [bind_session] + core_subs + binary_subs
        for msg in all_msgs:
            print(f"Sending initial subscription: Table {msg.split('LS_table=')[1].split('&')[0] if 'LS_table=' in msg else 'bind'}")
            await ws.send(msg)
            await asyncio.sleep(0.1)
        
        print(f"[+] Sent {len(all_msgs)} initial subscriptions")

    async def send_strike_subscriptions(self, ws, market_mapping):
        """Send strike subscriptions for each epic"""
        print(f"\n[+] Starting strike subscriptions from table {self.table_counter}")
        
        total_strikes = 0
        for market_id, underlying_epics in market_mapping.items():
            for underlying_epic, epics in underlying_epics.items():
                for epic in epics:
                    # URL encode the epic for the subscription
                    encoded_epic = epic.replace(".", "%2E").replace("-", "%2D")
                    
                    strike_msg1 = (
                        "control\r\n"
                        f"LS_mode=MERGE&LS_id=V2-F-BD1%2CAK1%2CBS1%2CAS1%2CUTM%2CDLY%2CUBS%2CSWAP_3_SHORT%2CSWAP_3_LONG%7C{encoded_epic}&"
                        "LS_schema=displayOffer%20displayBid%20bidSize%20offerSize%20updateTime%20delayTime%20marketStatus%20swapPointSell%20swapPointBuy&"
                        f"LS_snapshot=true&LS_requested_max_frequency=1&LS_table={self.table_counter}&"
                        f"LS_req_phase={self.req_phase_counter}&LS_win_phase={self.win_phase}&LS_op=add&LS_session={self.session_id}&"
                    )
                    
                    print(f"Sending strike subscription: Table {self.table_counter}, Epic: {epic}")
                    await ws.send(strike_msg1)
                    await asyncio.sleep(0.05)  # Small delay between messages
                    
                    # Increment counters
                    self.table_counter += 1
                    self.req_phase_counter += 1
                    total_strikes += 1

                    strike_msg2 = (
                        "control\r\n"
                        f"LS_mode=MERGE&LS_id=V2-F-BD1%2CAK1%2CBS1%2CAS1%2CBD2%2CAK2%2CBS2%2CAS2%2CBD3%2CAK3%2CBS3%2CAS3%2CBD4%2CAK4%2CBS4%2CAS4%2CBD5%2CAK5%2CBS5%2CAS5%7C{encoded_epic}&"
                        "LS_schema=displayOffer%20displayBid%20bidSize%20offerSize%20displayOffer2%20displayBid2%20bidSize2%20offerSize2%20displayOffer3%20displayBid3%20bidSize3%20offerSize3%20displayOffer4%20displayBid4%20bidSize4%20offerSize4%20displayOffer5%20displayBid5%20bidSize5%20offerSize5&"
                        f"LS_snapshot=true&LS_requested_max_frequency=1&LS_table={self.table_counter}&"
                        f"LS_req_phase={self.req_phase_counter}&LS_win_phase={self.win_phase}&LS_op=add&LS_session={self.session_id}&"
                    )
                    
                    print(f"Sending BID ASK subscription: Table {self.table_counter}, Epic: {epic}")
                    await ws.send(strike_msg2)
                    await asyncio.sleep(0.05)  # Small delay between messages
                    
                    # Increment counters
                    self.table_counter += 1
                    self.req_phase_counter += 1
        
        print(f"[+] Sent {total_strikes} strike subscriptions")

    async def send_hierarchy_subscriptions(self, ws, forex_ids):
        """Send hierarchy subscriptions for each forex ID"""
        print(f"\n[+] Starting hierarchy subscriptions from table {self.table_counter}")
        
        for forex_id in forex_ids:
            hier_msg = (
                "control\r\n"
                f"LS_mode=RAW&LS_id=M___.MGE%7CHIER-{forex_id}-JSON&LS_schema=json&"
                f"LS_requested_max_frequency=1&LS_table={self.table_counter}&"
                f"LS_req_phase={self.req_phase_counter}&LS_win_phase={self.win_phase}&LS_op=add&LS_session={self.session_id}&"
            )
            
            print(f"Sending hierarchy subscription: Table {self.table_counter}, ID: {forex_id}")
            await ws.send(hier_msg)
            await asyncio.sleep(0.1)
            
            # Increment counters
            self.table_counter += 1
            self.req_phase_counter += 1
        
        print(f"[+] Sent {len(forex_ids)} hierarchy subscriptions")

def print_market_mapping(market_mapping):
    """Print the market mapping in a readable format"""
    print("\n" + "="*60)
    print("MARKET MAPPING SUMMARY")
    print("="*60)
    
    for market_id, underlying_epics in market_mapping.items():
        print(f"\nMarket ID: {market_id}")
        for underlying_epic, epics in underlying_epics.items():
            print(f"  Underlying Epic: {underlying_epic}")
            print(f"    Epics ({len(epics)}):")
            for epic in epics:
                print(f"      - {epic}")
    
    # Summary statistics
    total_underlying = sum(len(underlying_epics) for underlying_epics in market_mapping.values())
    total_epics = sum(len(epics) for underlying_epics in market_mapping.values() 
                     for epics in underlying_epics.values())
    
    print(f"\n[+] Summary: {len(market_mapping)} market IDs, {total_underlying} underlying epics, {total_epics} total epics")

async def listen():
    # Get session info and market data
    session_info = get_session_info()
    session_id = session_info["session_id"]
    phase = session_info["phase"]
    host = session_info["host"]
    phase = str((int(phase) + 2))

    print(f"[+] Session ID: {session_id}")
    print(f"[+] Phase: {phase}")
    print(f"[+] Host: {host}")

    # Fetch and process market data
    market_tree = fetch_market_tree()
    forex_ids = extract_forex_ids(market_tree)
    
    if not forex_ids:
        print("[-] No Forex markets found under '5 Minute Binaries'.")
        return
    
    print(f"[+] Found {len(forex_ids)} forex market IDs: {forex_ids}")
    
    # Map market data
    market_mapping = map_market_data(forex_ids)
    print_market_mapping(market_mapping)
    
    # Connect to WebSocket
    uri = f"wss://{host}/lightstreamer"
    print(f"\n[+] Connecting to {uri}")
    
    ws_manager = WebSocketManager(session_id, phase, host)
    
    async with websockets.connect(uri, subprotocols=["js.lightstreamer.com"]) as ws:
        print("[+] WebSocket connected")
        
        # Send initial subscriptions (tables 1-14)
        await ws_manager.send_initial_subscriptions(ws)
        
        # Send strike subscriptions for all epics
        await ws_manager.send_strike_subscriptions(ws, market_mapping)
        
        # Send hierarchy subscriptions
        await ws_manager.send_hierarchy_subscriptions(ws, forex_ids)
        
        print("\n[+] All subscriptions sent. Listening for messages...")
        
        try:
            async for message in ws:
                if('z(30' in message):
                    print(message)
                if ('d(30' in message):
                    print("Updated:", message)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"[-] Connection closed: {e.code} {e.reason}")
        except KeyboardInterrupt:
            print("\n[+] Shutting down...")

if __name__ == "__main__":
    asyncio.run(listen())
# ---------------------------------------------------------------
# File        : config.py
# Author      : Shivam Garg
# Created on  : 27-06-2005

# Copyright (c) Shivam Garg. All rights reserved.
# ---------------------------------------------------------------

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Authentication
    NADEX_USERNAME = os.getenv('NADEX_USERNAME')
    NADEX_PASSWORD = os.getenv('NADEX_PASSWORD')
    NADEX_USER_ID = os.getenv('NADEX_USER_ID')
    
    # API URLs
    NADEX_AUTH_URL = os.getenv('NADEX_AUTH_URL')
    NADEX_SESSION_URL = os.getenv('NADEX_SESSION_URL')
    NADEX_MARKET_TREE_URL = os.getenv('NADEX_MARKET_TREE_URL')
    NADEX_NAVIGATION_URL = os.getenv('NADEX_NAVIGATION_URL')
    FRONTEND_PORT = os.getenv('FRONTEND_PORT')
    # WebSocket Configuration
    PING_INTERVAL = int(os.getenv('PING_INTERVAL', 30))
    RESUBSCRIBE_INTERVAL = int(os.getenv('RESUBSCRIBE_INTERVAL', 300))
    INITIAL_TABLE_COUNTER = int(os.getenv('INITIAL_TABLE_COUNTER', 15))
    INITIAL_REQ_PHASE_COUNTER = int(os.getenv('INITIAL_REQ_PHASE_COUNTER', 663))
    WIN_PHASE = int(os.getenv('WIN_PHASE', 63))

# Headers for authentication
AUTH_HEADERS = {
    "Accept": "application/json; charset=UTF-8",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://platform.nadex.com",
    "User-Agent": "Mozilla/5.0",
    "x-device-user-agent": "vendor=IG | applicationType=Nadex | platform=web | deviceType=phone | version=0.907.0+78b9f706"
}

# Headers for session creation
SESSION_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://platform.nadex.com",
    "Referer": "https://platform.nadex.com/",
    "User-Agent": "Mozilla/5.0"
}

# Headers for market data requests
MARKET_HEADERS = {
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
    "x-device-user-agent": "vendor=IG | applicationType=Nadex | platform=web | deviceType=phone | version=0.907.0+78b9f706"
}

# Navigation headers
NAVIGATION_HEADERS = {
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
    "x-device-user-agent": "vendor=IG | applicationType=Nadex | platform=web | deviceType=phone | version=0.907.0+78b9f706"
}

def get_auth_payload():
    """Get authentication payload with credentials from environment"""
    return {
        "username": Config.NADEX_USERNAME,
        "password": Config.NADEX_PASSWORD
    }

def get_session_payload(xst_token):
    """Get session creation payload"""
    return {
        "LS_phase": "2301",
        "LS_cause": "new.api",
        "LS_polling": "true",
        "LS_polling_millis": "0",
        "LS_idle_millis": "0",
        "LS_client_version": "6.1",
        "LS_adapter_set": "InVisionProvider",
        "LS_user": Config.NADEX_USER_ID,
        "LS_password": f"XST-{xst_token}",
        "LS_container": "lsc"
    }
import requests
import re
from collections import defaultdict

from config import (
    Config,
    AUTH_HEADERS,
    SESSION_HEADERS,
    MARKET_HEADERS,
    NAVIGATION_HEADERS,
    get_auth_payload,
    get_session_payload,
)

# Global XST token
xst_token = None

def get_xst_token():
    """Authenticate with Nadex and get XST token."""
    global xst_token
    print("[+] Authenticating with Nadex...")
    resp = requests.post(
        Config.NADEX_AUTH_URL,
        json=get_auth_payload(),
        headers=AUTH_HEADERS
    )
    resp.raise_for_status()
    token = resp.headers.get("x-security-token")
    if not token:
        raise RuntimeError("Missing x-security-token")
    xst_token = token
    print(f"[+] Obtained XST token: {token[:20]}…")
    return token

def get_session_info():
    """Create Lightstreamer session and return session info."""
    get_xst_token()
    print("[+] Creating Lightstreamer session…")
    resp = requests.post(
        Config.NADEX_SESSION_URL,
        data=get_session_payload(xst_token),
        headers=SESSION_HEADERS
    )
    resp.raise_for_status()
    body = resp.text
    sid = re.search(r"start\('([^']+)'", body).group(1)
    host = re.search(r"start\('[^']+',\s*'([^']+)'", body).group(1)
    phase = re.search(r"setPhase\((\d+)\);", body).group(1)
    return sid, host, int(phase)

def fetch_market_tree():
    """Fetch market tree from Nadex API."""
    if not xst_token:
        raise RuntimeError("xst_token not set")
    print("[+] Fetching market tree…")
    hdrs = {k: v for k, v in MARKET_HEADERS.items() if not k.startswith(":")}
    hdrs["x-security-token"] = xst_token
    resp = requests.get(Config.NADEX_MARKET_TREE_URL, headers=hdrs)
    resp.raise_for_status()
    print(f"[+] Market Tree status: {resp.status_code}")
    return resp.json()

def extract_forex_ids(tree):
    """Extract forex market IDs from market tree."""
    for node in tree.get("topLevelNodes", []):
        if node.get("name", "").lower() == "5 minute binaries":
            for c in node.get("children", []):
                if c.get("name", "").lower() == "forex":
                    return [x["id"] for x in c.get("children", [])]
    return []

def fetch_navigation_by_id(mid):
    """Fetch navigation data for a specific market ID."""
    url = f"{Config.NADEX_NAVIGATION_URL}/{mid}"
    hdrs = NAVIGATION_HEADERS.copy()
    hdrs["x-security-token"] = xst_token
    resp = requests.get(url, headers=hdrs)
    resp.raise_for_status()
    return resp.json()

def map_market_data(fx_ids):
    """Map market data from forex IDs to underlying epics."""
    mapping = defaultdict(lambda: defaultdict(list))
    for mid in fx_ids:
        print(f"⟳ Processing market ID {mid}")
        nav = fetch_navigation_by_id(mid)
        for m in nav.get("markets", []):
            ue = m.get("underlyingEpic", "")
            ep = m.get("epic", "")
            if ue and ep:
                mapping[mid][ue].append(ep)
        print(f"  → Found {len(nav.get('markets', []))} epics")
    return mapping

def print_market_mapping(mapping):
    """Print a summary of the market mapping."""
    print("\n" + "=" * 50 + "\nMARKET MAPPING SUMMARY\n" + "=" * 50)
    total_under, total_ep = 0, 0
    for mid, ueps in mapping.items():
        print(f"Market ID {mid}:")
        for ue, eps in ueps.items():
            print(f"  • {ue}: {len(eps)} epics")
            total_under += 1
            total_ep += len(eps)
    print(f"\n[+] {len(mapping)} markets, {total_under} underlyings, {total_ep} total epics")

def get_current_xst_token():
    """Get the current XST token."""
    return xst_token
import re
from collections import defaultdict

# Global table to epic mapping
table_to_epic = {}

# Regex to extract z() and d() calls
CALL_RE = re.compile(r"(z|d)\(\s*([^)]*?)\s*\)")

def update_table_mapping(epic, table_id, type):
    """
    Update the table_to_epic mapping when new subscriptions are made.
    Call this function whenever you process the subscription table from logs.
    """
    global table_to_epic
    
    table_to_epic[table_id] = epic + " " + type
    
    print(f"[INFO] Updated table mappings for {len(table_to_epic)} tables")

def parse_csv_args(argstr):
    """
    Parse comma-separated arguments, handling quoted strings properly.
    Returns list of cleaned argument strings.
    """
    # Handle quoted strings and regular comma separation
    tokens = re.findall(r"""'[^']*'|[^,]+""", argstr)
    # Strip whitespace and quotes, convert $ to empty string, # to None representation
    parts = []
    for token in tokens:
        cleaned = token.strip().strip("'")
        if cleaned == '$':
            parts.append('')  # Empty value
        elif cleaned == '#':
            parts.append(None)  # Null value
        else:
            parts.append(cleaned)
    
    return [p for p in parts if p is not None]  # Filter out None values

def find_time_field(parts, start_idx=3):
    """
    Find the timestamp field in the message parts.
    Looks for HH:MM:SS pattern starting from start_idx.
    """
    for i in range(start_idx, len(parts)):
        if parts[i] and re.match(r"\d{2}:\d{2}:\d{2}", str(parts[i])):
            return i, parts[i]
    return None, None

def process_forex_prices(msg: str):
    """
    Process underlying forex price updates (tables 8-14).
    These are the base currency pair prices that affect all options.
    """
    # Look for d() calls on tables 8-14 (forex underlying prices)
    forex_tables = {
        8: "AUD/USD",
        9: "EUR/USD", 
        10: "GBP/USD",
        11: "USD/JPY",
        12: "EUR/JPY",
        13: "GBP/JPY", 
        14: "USD/CAD"
    }
    
    for match in CALL_RE.finditer(msg):
        call_type, argstr = match.groups()
        if call_type != 'd':  # Only process updates for forex
            continue
            
        parts = parse_csv_args(argstr)
        if len(parts) < 3:
            continue
            
        try:
            tbl = int(parts[0])
        except (ValueError, TypeError):
            continue
            
        if tbl in forex_tables:
            price = parts[2] if len(parts) > 2 else "N/A"
            time_idx, timestamp = find_time_field(parts)
            if not timestamp:
                timestamp = "N/A"
                
            pair = forex_tables[tbl]
            print(f"[FOREX] {pair:8} -> {price:>10} @ {timestamp}")

def process_option_prices(msg: str):
    """
    Process binary option price updates.
    """
    for match in CALL_RE.finditer(msg):
        call_type, argstr = match.groups()
        parts = parse_csv_args(argstr)
        
        if len(parts) < 3:
            continue
            
        try:
            tbl = int(parts[0])
        except (ValueError, TypeError):
            continue
            
        epic = table_to_epic.get(tbl)
        if not epic:
            continue  # Not one of our tracked option tables
            
        # Extract key information
        item = parts[1] if len(parts) > 1 else "1"
        price = parts[2] if len(parts) > 2 else "N/A"
        
        # For z() calls, bid/ask are typically in positions 2,3
        # For d() calls, structure can vary
        if call_type == "z":
            # Initial price setting: z(tbl, item, bid, ask, size1, size2, time, ...)
            bid = parts[2] if len(parts) > 2 else "N/A"
            ask = parts[3] if len(parts) > 3 else "N/A" 
            time_idx, timestamp = find_time_field(parts, 4)
            tag = "INIT"
        else:  # 'd' call
            # Price update: d(tbl, item, price, [other_fields...], time, [more_fields...])
            bid = parts[2] if len(parts) > 2 else "N/A"
            ask = parts[3] if len(parts) > 3 else "N/A"
            time_idx, timestamp = find_time_field(parts)
            tag = "UPDATE"
            
        if not timestamp:
            timestamp = "N/A"
            
        # Clean up epic name for display
        epic_short = epic.replace("NB.I.", "").replace(".IP", "")
        
        print(f"[{tag:6}] {epic_short:35} bid={bid:>6} ask={ask:>6} @ {timestamp}")

def process_message(msg: str):
    """
    Main message processor that handles both forex and option updates.
    """
    # Process forex underlying prices first
    process_forex_prices(msg)
    
    # Then process option prices
    process_option_prices(msg)

def clear_table_mapping():
    """Clear the global table_to_epic mapping."""
    global table_to_epic
    table_to_epic.clear()
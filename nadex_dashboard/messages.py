from config import Config

class WebSocketMessages:
    """Class to handle all WebSocket message templates"""
    
    @staticmethod
    def get_bind_session_message(session_id, phase):
        """Generate bind session message (Table 1)"""
        return (
            "bind_session\r\n"
            f"LS_session={session_id}&LS_phase={phase}&LS_cause=loop1&LS_container=lsc&control\r\n"
            f"LS_mode=RAW&LS_id=M___.HB%7CHB.U.HEARTBEAT.IP&LS_schema=HEARTBEAT&"
            f"LS_requested_max_frequency=1&LS_table=1&LS_req_phase=619&LS_win_phase=50&LS_op=add&LS_session={session_id}&"
        )
    
    @staticmethod
    def get_core_subscriptions(session_id, user_id):
        """Generate core subscription messages (Tables 2-7)"""
        return [
            # Table 2 - Message Event Handler
            f"control\r\nLS_mode=RAW&LS_id=V2-M-MESSAGE_EVENT_HANDLER%7C{user_id}&LS_schema=message&"
            f"LS_requested_max_frequency=1&LS_table=2&LS_req_phase=620&LS_win_phase=50&LS_op=add&LS_session={session_id}&",

            # Table 3 - Account Balance
            f"control\r\nLS_mode=MERGE&LS_id=V2-AD-AC_AVAILABLE_BALANCE%2CAC_USED_MARGIN%7CACC.{user_id}&"
            f"LS_schema=AC_AVAILABLE_BALANCE%20AC_USED_MARGIN&LS_snapshot=true&LS_requested_max_frequency=1&"
            f"LS_table=3&LS_req_phase=621&LS_win_phase=50&LS_op=add&LS_session={session_id}&",

            # Table 4 - Message Event Handler JSON
            f"control\r\nLS_mode=RAW&LS_id=V2-M-MESSAGE_EVENT_HANDLER%7C{user_id}-OP-JSON&LS_schema=json&"
            f"LS_requested_max_frequency=1&LS_table=4&LS_req_phase=622&LS_win_phase=50&LS_op=add&LS_session={session_id}&",

            # Table 5 - MGE
            f"control\r\nLS_mode=RAW&LS_id=M___.MGE%7C{user_id}-LGT&LS_schema=message&"
            f"LS_requested_max_frequency=1&LS_table=5&LS_req_phase=623&LS_win_phase=50&LS_op=add&LS_session={session_id}&",

            # Table 6 - WO JSON
            f"control\r\nLS_mode=RAW&LS_id=V2-M-MESSAGE_EVENT_HANDLER%7C{user_id}-WO-JSON&LS_schema=json&"
            f"LS_requested_max_frequency=1&LS_table=6&LS_req_phase=624&LS_win_phase=50&LS_op=add&LS_session={session_id}&",

            # Table 7 - OH JSON
            f"control\r\nLS_mode=RAW&LS_id=V2-M-MESSAGE_EVENT_HANDLER%7C{user_id}-OH-JSON&LS_schema=json&"
            f"LS_requested_max_frequency=1&LS_table=7&LS_req_phase=625&LS_win_phase=50&LS_op=add&LS_session={session_id}&"
        ]
    
    @staticmethod
    def get_binary_fx_subscriptions(session_id):
        """Generate binary FX pairs subscriptions (Tables 8-14)"""
        pairs = [
            ("8", "SAUDUSD"),
            ("9", "SEURUSD"),
            ("10", "SGBPUSD"),
            ("11", "SUSDJPY"),
            ("12", "SEURJPY"),
            ("13", "SGBPJPY"),
            ("14", "SUSDCAD"),
        ]
        
        messages = []
        for table, symbol in pairs:
            phase_val = str(625 + int(table))
            msg = (
                "control\r\n"
                f"LS_mode=MERGE&LS_id=V2-F-LTP%2CUTM%7CCH.U.X%3A{symbol}:1321%3ABLD.OPT-1-1.IP&"
                "LS_schema=lastTradedPrice%20updateTime&LS_snapshot=true&LS_requested_max_frequency=1&"
                f"LS_table={table}&LS_req_phase={phase_val}&LS_win_phase=50&LS_op=add&LS_session={session_id}&"
            )
            messages.append(msg)
        
        return messages
    
    @staticmethod
    def get_strike_message_type1(session_id, encoded_epic, table_counter, req_phase_counter, win_phase):
        """Generate strike subscription message type 1"""
        return (
            "control\r\n"
            f"LS_mode=MERGE&LS_id=V2-F-BD1%2CAK1%2CBS1%2CAS1%2CUTM%2CDLY%2CUBS%2CSWAP_3_SHORT%2CSWAP_3_LONG%7C{encoded_epic}&"
            "LS_schema=displayOffer%20displayBid%20bidSize%20offerSize%20updateTime%20delayTime%20marketStatus%20swapPointSell%20swapPointBuy&"
            f"LS_snapshot=true&LS_requested_max_frequency=1&LS_table={table_counter}&"
            f"LS_req_phase={req_phase_counter}&LS_win_phase={win_phase}&LS_op=add&LS_session={session_id}&"
        )
    
    @staticmethod
    def get_strike_message_type2(session_id, encoded_epic, table_counter, req_phase_counter, win_phase):
        """Generate strike subscription message type 2 (BID/ASK)"""
        return (
            "control\r\n"
            f"LS_mode=MERGE&LS_id=V2-F-BD1%2CAK1%2CBS1%2CAS1%2CBD2%2CAK2%2CBS2%2CAS2%2CBD3%2CAK3%2CBS3%2CAS3%2CBD4%2CAK4%2CBS4%2CAS4%2CBD5%2CAK5%2CBS5%2CAS5%7C{encoded_epic}&"
            "LS_schema=displayOffer%20displayBid%20bidSize%20offerSize%20displayOffer2%20displayBid2%20bidSize2%20offerSize2%20displayOffer3%20displayBid3%20bidSize3%20offerSize3%20displayOffer4%20displayBid4%20bidSize4%20offerSize4%20displayOffer5%20displayBid5%20bidSize5%20offerSize5&"
            f"LS_snapshot=true&LS_requested_max_frequency=1&LS_table={table_counter}&"
            f"LS_req_phase={req_phase_counter}&LS_win_phase={win_phase}&LS_op=add&LS_session={session_id}&"
        )
    
    @staticmethod
    def get_hierarchy_message(session_id, forex_id, table_counter, req_phase_counter, win_phase):
        """Generate hierarchy subscription message"""
        return (
            "control\r\n"
            f"LS_mode=RAW&LS_id=M___.MGE%7CHIER-{forex_id}-JSON&LS_schema=json&"
            f"LS_requested_max_frequency=1&LS_table={table_counter}&"
            f"LS_req_phase={req_phase_counter}&LS_win_phase={win_phase}&LS_op=add&LS_session={session_id}&"
        )
    
    @staticmethod
    def get_ping_message(session_id, phase):
        """Generate ping/keepalive message"""
        return (
            f"control\r\nLS_op=constrain&LS_session={session_id}&LS_phase={phase}&LS_cause=keepalive&"
            f"LS_polling=true&LS_polling_millis=0&LS_idle_millis=0&LS_container=lsc&"
        )

class MessageTable:
    """Class to display message information in a table format"""
    
    def __init__(self):
        self.messages = []
    
    def add_message(self, message_type, table_id, description, epic=None):
        """Add a message to the table"""
        self.messages.append({
            'type': message_type,
            'table': table_id,
            'description': description,
            'epic': epic or 'N/A'
        })
    
    def print_table(self):
        """Print the message table"""
        print("\n" + "="*100)
        print("WEBSOCKET MESSAGE SUBSCRIPTION TABLE")
        print("="*100)
        print(f"{'Type':<20} {'Table':<8} {'Epic':<30} {'Description':<40}")
        print("-"*100)
        
        for msg in self.messages:
            print(f"{msg['type']:<20} {msg['table']:<8} {msg['epic']:<30} {msg['description']:<40}")
        
        print("-"*100)
        print(f"Total Messages: {len(self.messages)}")
        print("="*100)
    
    def clear(self):
        """Clear the message table"""
        self.messages = []

        
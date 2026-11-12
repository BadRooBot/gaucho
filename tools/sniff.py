#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaucho / Conquer II Mobile - Packet Sniffer & Logger
Hooks com.Tq.CQ2ClientAndroid (libCQ2ClientEn.so) to capture,
decode, and log all C2S and S2C game packets and actions in real time.
"""

import os
import sys
import time
import json
import struct
import datetime
import frida

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
NAMES_FILE = os.path.join(PROJECT_DIR, "mobile-packets-ids-names.txt")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
TXT_LOG = os.path.join(LOG_DIR, f"packets_{timestamp}.txt")
JSON_LOG = os.path.join(LOG_DIR, f"packets_{timestamp}.jsonl")

# Load packet ID names
PACKET_NAMES = {}
if os.path.exists(NAMES_FILE):
    with open(NAMES_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                try:
                    p_id = int(parts[0])
                    PACKET_NAMES[p_id] = parts[1].strip()
                except ValueError:
                    continue
print(f"[*] Loaded {len(PACKET_NAMES)} packet definitions from {os.path.basename(NAMES_FILE)}")

def extract_strings(raw_bytes, min_len=3):
    """Extract readable ASCII / UTF-8 strings from packet payload."""
    strings = []
    current = bytearray()
    for b in raw_bytes:
        if 32 <= b <= 126: # printable ASCII
            current.append(b)
        else:
            if len(current) >= min_len:
                try:
                    s = current.decode('utf-8', errors='ignore')
                    if not s.isspace():
                        strings.append(s)
                except Exception:
                    pass
            current = bytearray()
    if len(current) >= min_len:
        try:
            s = current.decode('utf-8', errors='ignore')
            if not s.isspace():
                strings.append(s)
        except Exception:
            pass
    return strings

def parse_packet_details(type_id, name, raw_bytes):
    """Parse special details for known packets (NPC talk, actions, etc.)."""
    details = {}
    size = len(raw_bytes)
    
    # Common strings
    strings = extract_strings(raw_bytes)
    if strings:
        details["strings"] = strings
    
    # Packet 2031 / 2032 (NPC dialog / Task / Action)
    if type_id in (2031, 2032): # CMsgTaskDialog
        if size >= 14:
            try:
                target_id = struct.unpack_from("<I", raw_bytes, 4)[0]
                action_type = raw_bytes[10]
                details["npc_id"] = target_id
                details["dialog_action"] = action_type
            except Exception:
                pass
                
    elif type_id == 10010: # CMsgAction
        if size >= 20:
            try:
                entity_id = struct.unpack_from("<I", raw_bytes, 4)[0]
                param = struct.unpack_from("<I", raw_bytes, 8)[0]
                action = struct.unpack_from("<H", raw_bytes, 12)[0]
                details["entity_id"] = entity_id
                details["param"] = param
                details["action"] = action
            except Exception:
                pass

    elif type_id == 10005: # CMsgWalk
        if size >= 12:
            try:
                entity_id = struct.unpack_from("<I", raw_bytes, 4)[0]
                direction = raw_bytes[8]
                mode = raw_bytes[9]
                details["entity_id"] = entity_id
                details["direction"] = direction
                details["mode"] = mode
            except Exception:
                pass

    return details

packet_counter = 0

def on_message(message, data):
    global packet_counter
    if message.get("type") == "send":
        p = message.get("payload", {})
        direction = p.get("dir", "???")
        type_id = p.get("type", 0)
        size = p.get("size", 0)
        raw_list = p.get("bytes", [])
        raw_bytes = bytes(raw_list) if raw_list else b""
        
        name = PACKET_NAMES.get(type_id, f"Unknown_{type_id}")
        details = parse_packet_details(type_id, name, raw_bytes)
        
        packet_counter += 1
        now_str = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        dir_tag = f"[{direction}]"
        if direction.startswith("C2S"):
            arrow = ">>> [CLIENT -> SERVER]"
        else:
            arrow = "<<< [SERVER -> CLIENT]"
            
        header = f"{now_str} #{packet_counter:04d} {arrow} Type: {type_id} (0x{type_id:04X} {name}) Size: {size}"
        print("=" * 80)
        print(header)
        
        if details.get("strings"):
            print(f"  [STRINGS]: {details['strings']}")
        if "npc_id" in details:
            print(f"  [NPC/ACTION]: NPC ID={details.get('npc_id')} Action={details.get('dialog_action')}")
        if "action" in details:
            print(f"  [ACTION]: Entity={details.get('entity_id')} Action={details.get('action')} Param={details.get('param')}")
            
        hex_preview = raw_bytes[:64].hex()
        if len(raw_bytes) > 64:
            hex_preview += "..."
        print(f"  [HEX]: {hex_preview}")
        
        # Log to TXT
        with open(TXT_LOG, "a", encoding="utf-8") as f:
            f.write(header + "\n")
            if details:
                f.write(f"  Details: {json.dumps(details, ensure_ascii=False)}\n")
            f.write(f"  Hex: {raw_bytes.hex()}\n\n")
            
        # Log to JSONL
        log_entry = {
            "seq": packet_counter,
            "time": now_str,
            "dir": direction,
            "type_id": type_id,
            "name": name,
            "size": size,
            "details": details,
            "hex": raw_bytes.hex()
        }
        with open(JSON_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
    elif message.get("type") == "log":
        print(f"[HOOK LOG] {message.get('payload')}")
    elif message.get("type") == "error":
        print(f"[HOOK ERROR] {message.get('description')}")
    else:
        print(f"[RAW MSG] {message}")

def find_target_pid(device, package_name="com.Tq.CQ2ClientAndroid"):
    # 1. Try frida enumerate_processes
    try:
        for p in device.enumerate_processes():
            if package_name in p.name:
                return p.pid
    except Exception:
        pass

    # 2. Query via ADB pidof
    import subprocess, re
    for adb_bin in ['C:\\LDPlayer\\LDPlayer9\\adb.exe', 'adb']:
        try:
            res = subprocess.run([adb_bin, 'shell', 'pidof', package_name], capture_output=True, text=True, timeout=5)
            # Find any integer PID in stdout
            pids = re.findall(r'\b\d{3,6}\b', res.stdout)
            if pids:
                return int(pids[-1])
        except Exception:
            continue
            
    # 3. Query via ps
    try:
        res = subprocess.run(['C:\\LDPlayer\\LDPlayer9\\adb.exe', 'shell', 'ps', '-ef'], capture_output=True, text=True, timeout=5)
        for line in res.stdout.splitlines():
            if package_name in line:
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    return int(parts[1])
    except Exception:
        pass

    return None

def main():
    print("-" * 80)
    print(" Conquer II Mobile (Gaucho) - Real-time Packet Sniffer & Logger")
    print("-" * 80)
    print(f"[*] Logging text output to: {TXT_LOG}")
    print(f"[*] Logging JSON output to: {JSON_LOG}")
    
    mgr = frida.get_device_manager()
    print("[*] Connecting to emulator frida-server at 192.168.1.6:27042...")
    device = mgr.add_remote_device("192.168.1.6:27042")
    
    target_pkg = "com.Tq.CQ2ClientAndroid"
    pid = find_target_pid(device, target_pkg)
    if not pid:
        # Try getting process by name directly
        try:
            pid = device.get_process(target_pkg).pid
        except Exception:
            pass
            
    if not pid:
        print(f"[!] Process {target_pkg} not found in process list. Checking via ADB...")
        import subprocess
        res = subprocess.run(['C:\\LDPlayer\\LDPlayer9\\adb.exe', 'shell', 'pidof', target_pkg], capture_output=True, text=True)
        out = res.stdout.strip()
        if out.isdigit():
            pid = int(out)
            
    if not pid:
        print(f"[-] ERROR: Could not find running process for {target_pkg}. Please ensure the game is open.")
        sys.exit(1)
        
    print(f"[+] Found game process: PID {pid}")
    print(f"[*] Attaching Frida to PID {pid}...")
    session = device.attach(pid)
    print("[+] Attached successfully!")
    
    js_file = os.path.join(BASE_DIR, "sniffer.js")
    with open(js_file, "r", encoding="utf-8") as f:
        js_code = f.read()
        
    script = session.create_script(js_code)
    script.on("message", on_message)
    print("[*] Loading sniffer script into game process...")
    script.load()
    
    # Inject packet names dictionary into JS
    try:
        count = script.exports_sync.set_packet_names(PACKET_NAMES)
        print(f"[+] Injected {count} packet definitions into JS hook engine.")
    except Exception as e:
        print(f"[!] Note: rpc set_packet_names: {e}")
        
    print("\n" + "=" * 80)
    print(">>> SNIFFER IS ACTIVE & RECORDING! <<<")
    print("You can now play, talk to NPCs, move, click buttons, or interact in game.")
    print("All packets will be printed here and saved to logs. Press Ctrl+C to stop.")
    print("=" * 80 + "\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopping sniffer...")
        session.detach()
        print(f"[+] Sniffer stopped. Logs saved successfully:\n  - {TXT_LOG}\n  - {JSON_LOG}")

if __name__ == "__main__":
    main()

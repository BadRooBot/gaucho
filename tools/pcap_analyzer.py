#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCAP Parser and Stream Analyzer for Conquer Mobile (Gaucho)
Parses Linux SLL and Ethernet PCAP captures, reconstructs TCP streams,
extracts packet types, strings, NPC dialogues, and hex dumps.
"""

import os
import sys
import struct
import json
import datetime
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
NAMES_FILE = os.path.join(PROJECT_DIR, "mobile-packets-ids-names.txt")

PACKET_NAMES = {}
if os.path.exists(NAMES_FILE):
    with open(NAMES_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0].isdigit():
                PACKET_NAMES[int(parts[0])] = parts[1].strip()

def extract_strings(data, min_len=3):
    strings = []
    cur = bytearray()
    for b in data:
        if 32 <= b <= 126:
            cur.append(b)
        else:
            if len(cur) >= min_len:
                try:
                    s = cur.decode("utf-8", errors="ignore")
                    if not s.isspace():
                        strings.append(s)
                except Exception:
                    pass
            cur = bytearray()
    if len(cur) >= min_len:
        try:
            s = cur.decode("utf-8", errors="ignore")
            if not s.isspace():
                strings.append(s)
        except Exception:
            pass
    return strings

def parse_pcap(pcap_path):
    if not os.path.exists(pcap_path):
        print(f"[-] PCAP file not found: {pcap_path}")
        return []

    with open(pcap_path, "rb") as f:
        gh = f.read(24)
        if len(gh) < 24:
            return []
        magic, v_maj, v_min, tz, sig, snaplen, link_type = struct.unpack("<IHHiIII", gh)
        endian = "<"
        if magic == 0xd4c3b2a1:
            endian = ">"
            magic, v_maj, v_min, tz, sig, snaplen, link_type = struct.unpack(">IHHiIII", gh)
        elif magic != 0xa1b2c3d4:
            print(f"[-] Unknown PCAP magic: 0x{magic:08x}")
            return []

        packets = []
        while True:
            ph = f.read(16)
            if len(ph) < 16:
                break
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(f"{endian}IIII", ph)
            pdata = f.read(incl_len)
            if len(pdata) < incl_len:
                break

            # Parse Link Layer
            ip_offset = 0
            if link_type == 113: # Linux SLL (Cooked)
                if len(pdata) < 16:
                    continue
                proto_type = struct.unpack(">H", pdata[14:16])[0]
                if proto_type != 0x0800: # IPv4
                    continue
                ip_offset = 16
            elif link_type == 1: # Ethernet
                if len(pdata) < 14:
                    continue
                proto_type = struct.unpack(">H", pdata[12:14])[0]
                if proto_type != 0x0800:
                    continue
                ip_offset = 14
            else:
                continue

            # Parse IPv4 Header
            if len(pdata) < ip_offset + 20:
                continue
            ip_header = pdata[ip_offset:ip_offset + 20]
            ihl = (ip_header[0] & 0x0f) * 4
            protocol = ip_header[9]
            if protocol != 6: # TCP only
                continue

            src_ip = ".".join(map(str, ip_header[12:16]))
            dst_ip = ".".join(map(str, ip_header[16:20]))

            # Parse TCP Header
            tcp_offset = ip_offset + ihl
            if len(pdata) < tcp_offset + 20:
                continue
            tcp_header = pdata[tcp_offset:tcp_offset + 20]
            src_port, dst_port, seq, ack = struct.unpack(">HHII", tcp_header[:12])
            tcp_hlen = ((tcp_header[12] >> 4) & 0x0f) * 4
            payload_offset = tcp_offset + tcp_hlen
            payload = pdata[payload_offset:]

            packets.append({
                "ts": ts_sec + ts_usec / 1_000_000.0,
                "src": f"{src_ip}:{src_port}",
                "dst": f"{dst_ip}:{dst_port}",
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "seq": seq,
                "payload": payload
            })

    return packets

def analyze_pcap_file(pcap_path, out_txt=None, out_json=None):
    packets = parse_pcap(pcap_path)
    print(f"[*] Parsed {len(packets)} TCP packets from {os.path.basename(pcap_path)}")

    # Group by stream
    streams = defaultdict(list)
    for p in packets:
        # Canonical stream key
        ep1 = (p["src_ip"], p["src_port"])
        ep2 = (p["dst_ip"], p["dst_port"])
        k = tuple(sorted([ep1, ep2]))
        streams[k].append(p)

    print(f"[*] Identified {len(streams)} distinct TCP streams.")

    lines_out = []
    json_entries = []

    for i, (k, stream_pkts) in enumerate(streams.items(), 1):
        ep1_str = f"{k[0][0]}:{k[0][1]}"
        ep2_str = f"{k[1][0]}:{k[1][1]}"
        total_bytes = sum(len(p["payload"]) for p in stream_pkts)
        pkts_with_data = [p for p in stream_pkts if len(p["payload"]) > 0]
        
        banner = f"\n{'='*78}\nSTREAM #{i}: {ep1_str} <---> {ep2_str} (Packets: {len(stream_pkts)}, Data Bytes: {total_bytes})\n{'='*78}"
        print(banner)
        lines_out.append(banner)

        for p in pkts_with_data:
            pl = p["payload"]
            size = len(pl)
            strings = extract_strings(pl)
            
            # Try parsing CQ2 header: [u16 len][u16 type]
            type_id = None
            pkt_name = ""
            if size >= 4:
                plen = pl[0] | (pl[1] << 8)
                ptype = pl[2] | (pl[3] << 8)
                if ptype in PACKET_NAMES:
                    type_id = ptype
                    pkt_name = PACKET_NAMES[ptype]

            dt = datetime.datetime.fromtimestamp(p["ts"]).strftime("%H:%M:%S.%f")[:-3]
            dir_str = f"{p['src']} -> {p['dst']}"
            desc = f"{dt} [{dir_str}] Len={size}"
            if type_id is not None:
                desc += f" Type={type_id} (0x{type_id:04X} {pkt_name})"

            print(desc)
            lines_out.append(desc)

            if strings:
                str_line = f"  [STRINGS]: {strings}"
                print(str_line)
                lines_out.append(str_line)

            hex_preview = pl[:64].hex()
            if len(pl) > 64:
                hex_preview += "..."
            print(f"  [HEX]: {hex_preview}")
            lines_out.append(f"  [HEX]: {hex_preview}")

            json_entries.append({
                "time": dt,
                "src": p["src"],
                "dst": p["dst"],
                "size": size,
                "type": type_id,
                "name": pkt_name,
                "strings": strings,
                "hex": pl.hex()
            })

    if out_txt:
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(lines_out) + "\n")
        print(f"\n[+] Saved text report to: {out_txt}")

    if out_json:
        with open(out_json, "w", encoding="utf-8") as f:
            for entry in json_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"[+] Saved JSON report to: {out_json}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_pcap = sys.argv[1]
    else:
        target_pcap = os.path.join(BASE_DIR, "captures", "latest.pcap")
    analyze_pcap_file(target_pcap)


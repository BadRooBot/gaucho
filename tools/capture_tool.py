#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Packet Capture & Analysis Tool for Conquer Mobile
Uses tcpdump on LDPlayer (100% stable, zero crash risk), pulls the PCAP,
and generates full packet & string reports.
"""

import os
import sys
import time
import subprocess
import datetime
from pcap_analyzer import analyze_pcap_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADB_PATH = r"C:\LDPlayer\LDPlayer9\adb.exe"
if not os.path.exists(ADB_PATH):
    ADB_PATH = "adb"

CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
os.makedirs(CAPTURES_DIR, exist_ok=True)

def run_adb(cmd_list):
    full_cmd = [ADB_PATH] + cmd_list
    return subprocess.run(full_cmd, capture_output=True, text=True)

def check_adb():
    res = run_adb(["devices"])
    if "device" not in res.stdout:
        print("[-] Error: LDPlayer emulator not detected or offline.")
        return False
    return True

def start_tcpdump():
    # Kill any existing tcpdump instances
    run_adb(["shell", "su 0 killall -9 tcpdump 2>/dev/null"])
    time.sleep(0.5)

    # Remove previous pcap
    run_adb(["shell", "su 0 rm -f /sdcard/game.pcap"])

    print("[*] Starting tcpdump in LDPlayer background...")
    # Start tcpdump listening on TCP traffic for Conquer
    cmd = [ADB_PATH, "shell", "su 0 /system/xbin/tcpdump -i any -s 0 -w /sdcard/game.pcap tcp"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)

    # Verify tcpdump is running
    res = run_adb(["shell", "su 0 pidof tcpdump"])
    pid = res.stdout.strip()
    if pid.isdigit() or len(pid.split()) > 0:
        print(f"[+] tcpdump is actively capturing (PID: {pid})!")
        return proc
    else:
        print("[-] Failed to start tcpdump on device.")
        return None

def stop_tcpdump(proc):
    print("\n[*] Stopping capture on device...")
    run_adb(["shell", "su 0 killall -2 tcpdump"])
    time.sleep(1.5)
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            pass

def main():
    print("=" * 78)
    print(" Conquer II Mobile - Network Packet Capture & REA Analyzer")
    print(" 100% Stable - Uses kernel-level tcpdump (Zero crash risk)")
    print("=" * 78)

    if not check_adb():
        sys.exit(1)

    proc = start_tcpdump()
    if not proc:
        sys.exit(1)

    print("\n" + "*" * 78)
    print(">>> RECORDING IN PROGRESS <<<")
    print(" You can now:")
    print("  1. Log into your account in the game.")
    print("  2. Talk to any NPC (e.g. Rebirth NPC, Rowland, etc.).")
    print("  3. Choose options, walk, fight, or perform any action.")
    print(" All packets and network streams are being recorded silently.")
    print("\n WHEN YOU ARE DONE, PRESS [ENTER] TO STOP & ANALYZE:")
    print("*" * 78 + "\n")

    try:
        input()
    except KeyboardInterrupt:
        pass

    stop_tcpdump(proc)

    # Pull PCAP from device
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    local_pcap = os.path.join(CAPTURES_DIR, f"capture_{timestamp}.pcap")
    local_txt = os.path.join(CAPTURES_DIR, f"report_{timestamp}.txt")
    local_json = os.path.join(CAPTURES_DIR, f"report_{timestamp}.jsonl")

    print(f"[*] Pulling /sdcard/game.pcap to {local_pcap}...")
    run_adb(["pull", "/sdcard/game.pcap", local_pcap])

    if not os.path.exists(local_pcap) or os.path.getsize(local_pcap) == 0:
        print("[-] Error: PCAP file is empty or was not pulled.")
        sys.exit(1)

    pcap_size = os.path.getsize(local_pcap)
    print(f"[+] Captured {pcap_size:,} bytes of network traffic!")

    # Analyze with pcap_analyzer
    print("\n[*] Analyzing captured streams and packets...")
    analyze_pcap_file(local_pcap, out_txt=local_txt, out_json=local_json)

    print("\n" + "=" * 78)
    print(">>> ANALYSIS COMPLETE! <<<")
    print(f"  - Full PCAP:        {local_pcap}")
    print(f"  - Formatted Report: {local_txt}")
    print(f"  - JSONL Stream:     {local_json}")
    print("=" * 78)

if __name__ == "__main__":
    main()


import subprocess, struct, sys, re

def get_pid():
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', 'pidof com.gaucho.game'], capture_output=True, text=True)
    out = p.stdout.strip()
    return out.split()[0] if out else None

def get_base(pid):
    cmd = f"su -c 'grep -m1 libCQ2ClientEn.so /proc/{pid}/maps'"
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', cmd], capture_output=True, text=True)
    m = re.match(r'^([0-9a-fA-F]+)-', p.stdout.strip())
    return int(m.group(1), 16) if m else None

def read_mem(pid, addr, size):
    cmd = f"su -c 'dd if=/proc/{pid}/mem bs=1 skip={addr} count={size} 2>/dev/null'"
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', cmd], capture_output=True)
    return p.stdout

def main():
    pid = get_pid()
    if not pid:
        print("com.gaucho.game not running")
        return
    base = get_base(pid)
    if not base:
        print(f"libCQ2ClientEn.so not loaded in PID {pid}")
        return
    print(f"PID: {pid}, Base: 0x{base:08x}")
    
    # g_game_state @ base + 0x02eeef80
    st_bytes = read_mem(pid, base + 0x02eeef80, 4)
    if len(st_bytes) == 4:
        val = struct.unpack('<I', st_bytes)[0]
        print(f"g_game_state = {val}")
    
    # g_i_want_to_login @ base + 0x02eeef9c
    login_bytes = read_mem(pid, base + 0x02eeef9c, 1)
    if len(login_bytes) == 1:
        print(f"g_i_want_to_login = {login_bytes[0]}")

    # s_nMaxPrgValue @ base + 0x02ef4580
    prg_bytes = read_mem(pid, base + 0x02ef4580, 8)
    if len(prg_bytes) == 8:
        max_val, speed = struct.unpack('<II', prg_bytes)
        print(f"s_nMaxPrgValue = {max_val} (0x{max_val:x}), s_nSpeed = {speed}")
    else:
        print("Failed to read s_nMaxPrgValue")

    # innerPtr @ base + 0x02e99894
    inner_bytes = read_mem(pid, base + 0x02e99894, 4)
    if len(inner_bytes) == 4:
        mgr = struct.unpack('<I', inner_bytes)[0]
        print(f"innerPtr (mgr) = 0x{mgr:08x}")
        if mgr != 0:
            mgr_bytes = read_mem(pid, mgr, 64)
            print("mgr bytes (0..64):")
            for i in range(0, len(mgr_bytes), 16):
                chunk = mgr_bytes[i:i+16]
                hex_str = ' '.join(f'{b:02x}' for b in chunk)
                print(f"  +{i:02x}: {hex_str}")
    else:
        print("Failed to read innerPtr")

if __name__ == '__main__':
    main()

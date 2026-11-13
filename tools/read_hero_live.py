import subprocess, struct, re

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
        print("not running")
        return
    base = get_base(pid)
    print(f"PID: {pid}, Base: 0x{base:08x}")
    speed_ptr_bytes = read_mem(pid, base + 0x02dbdc64, 4)
    max_ptr_bytes = read_mem(pid, base + 0x02dbdc68, 4)
    speed_ptr = struct.unpack('<I', speed_ptr_bytes)[0]
    max_ptr = struct.unpack('<I', max_ptr_bytes)[0]
    print(f"Runtime speed_ptr = 0x{speed_ptr:08x} (offset base + 0x{speed_ptr - base:08x})")
    print(f"Runtime max_ptr   = 0x{max_ptr:08x} (offset base + 0x{max_ptr - base:08x})")
    speed_val = struct.unpack('<I', read_mem(pid, speed_ptr, 4))[0]
    max_val = struct.unpack('<I', read_mem(pid, max_ptr, 4))[0]
    print(f"Runtime s_nSpeed = {speed_val}")
    print(f"Runtime s_nMaxPrgValue = {max_val} (0x{max_val:x})")

    inner_ptr_bytes = read_mem(pid, base + 0x02e99894, 4)
    mgr = struct.unpack('<I', inner_ptr_bytes)[0]
    print(f"inner_ptr (base + 0x02e99894) = 0x{base + 0x02e99894:08x}, mgr = 0x{mgr:08x}")
    if mgr != 0:
        mgr_data = read_mem(pid, mgr, 40)
        print("mgr_data: " + " ".join(f"{b:02x}" for b in mgr_data))
        print(f"mgr+0x18 (isInit): {mgr_data[0x18]}")
        print(f"mgr+0x08 (flags): " + " ".join(f"{b:02x}" for b in mgr_data[8:24]))

if __name__ == '__main__':
    main()

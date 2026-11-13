import subprocess, struct, re

def get_pid():
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', 'pidof com.gaucho.game'], capture_output=True, text=True)
    out = p.stdout.strip()
    return out.split()[0] if out else None

def get_base(pid):
    cmd = "su -c 'grep -m1 libCQ2ClientEn.so /proc/" + pid + "/maps'"
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', cmd], capture_output=True, text=True)
    m = re.match(r'^([0-9a-fA-F]+)-', p.stdout.strip())
    return int(m.group(1), 16) if m else None

def read_mem(pid, addr, size):
    cmd = f"su -c 'dd if=/proc/{pid}/mem bs=1 skip={addr} count={size} 2>/dev/null'"
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', cmd], capture_output=True)
    return p.stdout

def main():
    pid = get_pid()
    base = get_base(pid)
    targets = [0x02dba160, 0x02db9118, 0x02dba158, 0x02dba140, 0x02dbaf7c]
    for t in targets:
        raw = read_mem(pid, base + t, 4)
        if len(raw) == 4:
            val = struct.unpack('<I', raw)[0]
            print(f"0x{t:08x}: runtime val = 0x{val:08x}")
            # if val is pointer to string or struct
            if 0x10000000 <= val <= 0xffffffff:
                s = read_mem(pid, val, 64)
                print(f"  deref: {s}")

if __name__ == '__main__':
    main()

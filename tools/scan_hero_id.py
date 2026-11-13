import subprocess, struct, re

def get_pid():
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', 'pidof com.gaucho.game'], capture_output=True, text=True)
    out = p.stdout.strip()
    return out.split()[0] if out else None

def main():
    pid = get_pid()
    if not pid:
        print("not running")
        return
    # Read maps
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', f"su -c 'grep \"rw-p\" /proc/{pid}/maps'"], capture_output=True, text=True)
    maps = []
    for line in p.stdout.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 2:
            rng = parts[0].split('-')
            start = int(rng[0], 16)
            end = int(rng[1], 16)
            name = parts[-1] if len(parts) >= 6 else ""
            maps.append((start, end, name))
    
    print(f"Scanning {len(maps)} rw-p mappings in PID {pid} for hero id 1300006 (0x13d626)...")
    needle = struct.pack('<I', 1300006)
    
    for start, end, name in maps:
        sz = end - start
        if sz > 20 * 1024 * 1024: # skip huge heaps for now
            continue
        cmd = f"su -c 'dd if=/proc/{pid}/mem bs=1024k skip={start//1024//1024} count={max(1, sz//1024//1024)} 2>/dev/null'"
        # Read directly using python on device or dd
        # Let's use a small python script executed via adb shell python or python locally
        pass

if __name__ == '__main__':
    main()


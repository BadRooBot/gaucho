import subprocess

def main():
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', 'pidof com.gaucho.game'], capture_output=True, text=True)
    pid = p.stdout.strip().split()[0]
    print(f'PID: {pid}')
    cmd = f'grep lib /proc/{pid}/maps'
    p2 = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', f'su 0 sh -c "{cmd}"'], capture_output=True, text=True)
    libs = set()
    for line in p2.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 6:
            libs.add(parts[5])
    for lib in sorted(libs):
        if 'gaucho' in lib or 'CQ2' in lib:
            print(lib)

if __name__ == '__main__':
    main()

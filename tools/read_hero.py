import subprocess, struct

addr = 0x05fc8580
cmd = f"su -c 'dd if=/proc/2952/mem bs=1 skip={addr} count=8 2>/dev/null'"
p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', cmd], capture_output=True)
if len(p.stdout) == 8:
    max_val, speed = struct.unpack('<II', p.stdout)
    print(f's_nMaxPrgValue = {max_val}, s_nSpeed = {speed}')
else:
    print(f'read failed, got len={len(p.stdout)}')

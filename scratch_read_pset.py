import subprocess, struct

pid = '5592'
base = 0xbf1d5000
addr = base + 0x02e990d0
cmd = f"su -c 'dd if=/proc/{pid}/mem bs=1 skip={addr} count=4 2>/dev/null'"
p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', cmd], capture_output=True)
ptr = struct.unpack('<I', p.stdout)[0]
print(f'CGamePlayerSet instance = 0x{ptr:08x}')

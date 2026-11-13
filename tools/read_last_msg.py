import subprocess, struct, re

def get_pid():
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', 'pidof com.gaucho.game'], capture_output=True, text=True)
    return p.stdout.strip().split()[0]

def get_base(pid):
    cmd = "su -c 'grep -m1 libCQ2ClientEn.so /proc/" + pid + "/maps'"
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', cmd], capture_output=True, text=True)
    m = re.match(r'^([0-9a-fA-F]+)-', p.stdout.strip())
    return int(m.group(1), 16)

def read_mem(pid, addr, size):
    cmd = f"su -c 'dd if=/proc/{pid}/mem bs=1 skip={addr} count={size} 2>/dev/null'"
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', cmd], capture_output=True)
    return p.stdout

pid = get_pid()
base = get_base(pid)
txtmsg_set = base + 0x2e99f14 + 8

data = read_mem(pid, txtmsg_set, 48)
words = struct.unpack('<12I', data)
read_idx = words[1] # +4
ptr_table = words[4] # +0x10
base_idx = words[7] # +0x1c
write_idx = words[8] # +0x20
print(f'read_idx={read_idx}, write_idx={write_idx}, ptr_table={ptr_table:#x}, base_idx={base_idx}')

idx = 0
r0 = base_idx + idx
r1 = r0 >> 10
r0_off = r0 & 0x3ff

tbl1_raw = read_mem(pid, ptr_table + r1 * 4, 4)
tbl1 = struct.unpack('<I', tbl1_raw)[0]
msg_ptr_raw = read_mem(pid, tbl1 + r0_off * 4, 4)
msg_ptr = struct.unpack('<I', msg_ptr_raw)[0]
print(f'msg_ptr = {msg_ptr:#x}')

msg_bytes = read_mem(pid, msg_ptr, 128)
print('raw bytes:', msg_bytes[:64])
try:
    print('utf-32:', msg_bytes.decode('utf-32', errors='ignore'))
except Exception as e:
    print(e)

import subprocess, struct, re

def get_pid():
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', 'pidof com.gaucho.game'], capture_output=True, text=True)
    return p.stdout.strip().split()[0]

def get_base(pid):
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', f'su -c "grep -m1 libCQ2ClientEn.so /proc/{pid}/maps"'], capture_output=True, text=True)
    m = re.match(r'^([0-9a-fA-F]+)-', p.stdout.strip())
    return int(m.group(1), 16)

def read_mem(pid, addr, size):
    p = subprocess.run(['adb', '-s', 'emulator-5554', 'shell', f'su -c "dd if=/proc/{pid}/mem bs=1 skip={addr} count={size} 2>/dev/null"'], capture_output=True)
    return p.stdout

pid = get_pid()
base = get_base(pid)
addr = base + 0x2e99f14
print(f"g_objEntrance at: {addr:#x}")
data = read_mem(pid, addr, 64)
words = struct.unpack('<16I', data)
for i, w in enumerate(words):
    print(f"  +{i*4:02x}: {w:#010x}")

# Check if vector has elements:
# vector usually is (start, finish, end_of_storage) at +8, +12, +16
v_start, v_finish, v_end = words[2], words[3], words[4]
print(f"vector: start={v_start:#x}, finish={v_finish:#x}, end={v_end:#x}")
if v_finish > v_start:
    count = (v_finish - v_start) // 12 # or sizeof(std::wstring) which in libc++ is 12 or 24?
    print(f"elements bytes: {v_finish - v_start}")
    raw_vec = read_mem(pid, v_start, v_finish - v_start)
    print("vector raw hex:", raw_vec.hex())


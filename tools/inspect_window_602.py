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

pid = get_pid()
base = get_base(pid)
print(f"PID: {pid}, Base: 0x{base:08x}")

# CQUIManager pInstance_E @ base + 0x2ef06a4
mgr_ptr_bytes = read_mem(pid, base + 0x2ef06a4, 4)
if len(mgr_ptr_bytes) != 4:
    print("Failed to read pInstance_E")
    exit()

mgr = struct.unpack('<I', mgr_ptr_bytes)[0]
print(f"CQUIManager instance = 0x{mgr:08x}")
if mgr == 0:
    exit()

# List windows:
# In CQUIManager:
# r2 = mgr + 4
# r3 = mgr + 8
# node = [r3]
# while node != r2:
#   id = [node + 8]
#   pWin = [node + 0xc]
#   node = [node + 4]
head_bytes = read_mem(pid, mgr + 8, 4)
node = struct.unpack('<I', head_bytes)[0]
end_node = mgr + 4
print(f"Walking window list from 0x{node:08x} to 0x{end_node:08x}...")

found_windows = {}
while node != 0 and node != end_node and len(found_windows) < 100:
    node_data = read_mem(pid, node, 16)
    if len(node_data) < 16: break
    prev_ptr, next_ptr, w_id, p_win = struct.unpack('<IIII', node_data)
    found_windows[w_id] = (p_win, node)
    node = next_ptr

print(f"Total open windows: {len(found_windows)}")
for w_id, (p_win, n_addr) in sorted(found_windows.items()):
    print(f"  Window {w_id}: pWin=0x{p_win:08x} (node=0x{n_addr:08x})")

if 602 in found_windows:
    p602 = found_windows[602][0]
    print(f"\nWindow 602 (CFDlgLoading) at 0x{p602:08x}:")
    d602 = read_mem(pid, p602, 0x300)
    # m_nProgress at +0x280
    # m_nState at +0x28c
    prog = struct.unpack('<I', d602[0x280:0x284])[0]
    state = struct.unpack('<I', d602[0x28c:0x290])[0]
    print(f"  m_nProgress = {prog} (0x{prog:x})")
    print(f"  m_nState = {state}")
else:
    print("\nWindow 602 is NOT in CQUIManager window list!")

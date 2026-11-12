import subprocess, struct

def read_mem(pid, addr, size):
    cmd = ['adb', 'shell', 'su', '-c', f'dd if=/proc/{pid}/mem bs=1 skip={addr} count={size} 2>/dev/null']
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout

base = 0x030d4000
inner_ptr_addr = base + 0x02e99894
data = read_mem(4929, inner_ptr_addr, 4)
print('inner_ptr raw bytes:', data.hex())
if len(data) == 4:
    ptr = struct.unpack('<I', data)[0]
    print(f'CNewFunctionOpenMgr instance at: 0x{ptr:08x}')
    if ptr != 0:
        mgr_data = read_mem(4929, ptr, 0x30)
        print('CNewFunctionOpenMgr memory:', mgr_data.hex())
        if len(mgr_data) >= 0x20:
            print('m_bInitStatus (offset 0x18):', mgr_data[0x18])
            flag = struct.unpack('<Q', mgr_data[8:16])[0]
            print(f'm_nFunctionFlag (offset 0x8): 0x{flag:016x}')

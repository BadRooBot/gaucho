import subprocess

def write_mem(pid, addr, data_bytes):
    # write to /sdcard/patch.bin
    with open('patch.bin', 'wb') as f:
        f.write(data_bytes)
    subprocess.run(['adb', 'push', 'patch.bin', '/data/local/tmp/patch.bin'])
    cmd = ['adb', 'shell', 'su', '0', 'dd', 'if=/data/local/tmp/patch.bin', f'of=/proc/{pid}/mem', 'bs=1', f'seek={addr}', f'count={len(data_bytes)}', 'conv=notrunc']
    subprocess.run(cmd)

def read_mem(pid, addr, size):
    cmd = ['adb', 'shell', 'su', '0', 'dd', f'if=/proc/{pid}/mem', 'bs=1', f'skip={addr}', f'count={size}', '2>/dev/null']
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout

pid = 23861
addr = 0xec3a0d98

print('Before:', read_mem(pid, addr, 1).hex())
write_mem(pid, addr, b'\x01')
print('After:', read_mem(pid, addr, 1).hex())


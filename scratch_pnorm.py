import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x014a3084
print(f'Scanning for references to 0x{target:08x}...')
for i in range(0, len(data)-4, 4):
    w = struct.unpack('<I', data[i:i+4])[0]
    if w in (target, target + 1):
        print(f'Pointer at 0x{i:08x}: 0x{w:08x}')

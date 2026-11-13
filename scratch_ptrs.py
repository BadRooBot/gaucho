import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target1 = 0x014a2bc0
target2 = 0x014a2bc1

for i in range(0, len(data)-4, 4):
    w = struct.unpack('<I', data[i:i+4])[0]
    if w in (target1, target2):
        print(f'Pointer at 0x{i:08x}: 0x{w:08x}')


import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x00f6df08
print(f"Scanning for branches to 0x{target:08x}...")
for i in range(0, len(data)-4, 2):
    w1, w2 = struct.unpack('<HH', data[i:i+4])
    if (w1 & 0xf800) == 0xf000 and (w2 & 0xd000) == 0x9000:
        cond = (w1 >> 6) & 0xf
        s = (w1 >> 10) & 1
        j1 = (w2 >> 13) & 1
        j2 = (w2 >> 11) & 1
        imm6 = w1 & 0x3f
        imm11 = w2 & 0x7ff
        offset = (s << 20) | (j2 << 19) | (j1 << 18) | (imm6 << 12) | (imm11 << 1)
        if s: offset -= (1 << 21)
        dest = (i + 4 + offset) & 0xffffffff
        if abs(dest - target) <= 8:
            print(f'B<cond>.W at 0x{i:08x} -> 0x{dest:08x}')
    if (w1 & 0xf800) == 0xf000 and (w2 & 0xd000) == 0xb000:
        s = (w1 >> 10) & 1
        j1 = (w2 >> 13) & 1
        j2 = (w2 >> 11) & 1
        imm10 = w1 & 0x3ff
        imm11 = w2 & 0x7ff
        i1 = ~(j1 ^ s) & 1
        i2 = ~(j2 ^ s) & 1
        offset = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s: offset -= (1 << 25)
        dest = (i + 4 + offset) & 0xffffffff
        if abs(dest - target) <= 8:
            print(f'B.W at 0x{i:08x} -> 0x{dest:08x}')


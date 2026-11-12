import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x01107e72
for i in range(0, len(data)-4, 2):
    w1, w2 = struct.unpack('<HH', data[i:i+4])
    if (w1 & 0xf800) == 0xf000 and (w2 & 0xd000) == 0xd000:
        s = (w1 >> 10) & 1
        j1 = (w2 >> 13) & 1
        j2 = (w2 >> 11) & 1
        imm10 = w1 & 0x3ff
        imm11 = w2 & 0x7ff
        i1 = ~(j1 ^ s) & 1
        i2 = ~(j2 ^ s) & 1
        offset = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            offset -= (1 << 25)
        pc = i + 4
        dest = (pc + offset) & 0xffffffff
        if dest == target or dest == target + 1:
            print(f'BL call at 0x{i:08x} -> 0x{dest:08x}')


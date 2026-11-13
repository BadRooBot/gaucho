import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x00d8cfdc
print(f'Scanning callers of PLT 0x{target:08x}...')

# Thumb BL/BLX
for i in range(0, len(data)-4, 2):
    w1, w2 = struct.unpack('<HH', data[i:i+4])
    # BL or BLX
    if (w1 & 0xf800) == 0xf000 and ((w2 & 0xd000) == 0xd000 or (w2 & 0xd001) == 0xc000):
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
        if (w2 & 0x1000) == 0: # BLX
            dest &= ~3
        if dest == target:
            print(f'Thumb call at 0x{i:08x}')

# ARM BL/BLX
for i in range(0, len(data)-4, 4):
    word = struct.unpack('<I', data[i:i+4])[0]
    if (word & 0x0e000000) == 0x0a000000: # BL
        imm24 = word & 0x00ffffff
        if imm24 & 0x800000: imm24 -= 0x1000000
        dest = (i + 8 + (imm24 << 2)) & 0xffffffff
        if dest == target:
            print(f'ARM call at 0x{i:08x}')


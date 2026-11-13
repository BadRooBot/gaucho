import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x0160cbf0
print(f'Scanning for branches to 0x{target:08x}...')

# Search in the range 0x0160b000 - 0x0160d000
for i in range(0x0160b000, 0x0160d000, 2):
    # Check conditional or unconditional Thumb branch
    w = struct.unpack('<H', data[i:i+2])[0]
    # B.N (e000)
    if (w & 0xf800) == 0xe000:
        imm11 = w & 0x7ff
        if imm11 & 0x400: imm11 -= 0x800
        dest = (i + 4 + (imm11 << 1)) & 0xffffffff
        if dest == target:
            print(f'B.N from 0x{i:08x}')
    # Bcc (d000)
    if (w & 0xf000) == 0xd000 and (w & 0x0f00) < 0x0e00:
        imm8 = w & 0xff
        if imm8 & 0x80: imm8 -= 0x100
        dest = (i + 4 + (imm8 << 1)) & 0xffffffff
        if dest == target:
            print(f'Bcc from 0x{i:08x}')

# Also check 32-bit branches
for i in range(0x0160b000, 0x0160d000, 2):
    w1, w2 = struct.unpack('<HH', data[i:i+4])
    # B.W
    if (w1 & 0xf800) == 0xf000 and (w2 & 0xd000) == 0x9000:
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
        if dest == target:
            print(f'B.W from 0x{i:08x}')

# Check TBB/TBH tables in the vicinity
# TBB [pc, rm] or TBH [pc, rm, lsl #1]
for i in range(0x0160b000, 0x0160cbf0, 2):
    w = struct.unpack('<H', data[i:i+2])[0]
    if (w & 0xfff0) == 0xe8d0: # TBB or TBH
        print(f'TBB/TBH at 0x{i:08x}')

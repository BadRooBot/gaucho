import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x00d0f714
print(f"Scanning for calls to PLT 0x{target:08x}...")
# Scan ARM BL / BLX
for i in range(0, len(data)-4, 4):
    word = struct.unpack('<I', data[i:i+4])[0]
    # ARM BL: cond 1011 imm24
    if (word & 0x0f000000) == 0x0b000000:
        imm24 = word & 0x00ffffff
        if imm24 & 0x800000:
            imm24 -= 0x1000000
        offset = imm24 << 2
        dest = (i + 8 + offset) & 0xffffffff
        if dest == target:
            print(f'ARM BL at 0x{i:08x}')
    # ARM BLX: 1111 101H imm24
    if (word & 0xfe000000) == 0xfa000000:
        h = (word >> 24) & 1
        imm24 = word & 0x00ffffff
        if imm24 & 0x800000:
            imm24 -= 0x1000000
        offset = (imm24 << 2) | (h << 1)
        dest = (i + 8 + offset) & 0xffffffff
        if dest == target:
            print(f'ARM BLX at 0x{i:08x}')

# Also check if target is called via GOT pointer (LDR)
target_got = 0x02dd6d3c
for i in range(0, len(data)-4, 4):
    w = struct.unpack('<I', data[i:i+4])[0]
    if w == target_got:
        print(f'Reference to GOT at 0x{i:08x}')

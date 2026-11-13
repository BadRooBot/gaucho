import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x00d56190
# In Thumb-2:
# 32-bit branch:
# hw1: 1111 0 S imm10
# hw2 for blx: 11 1 J1 0 J2 imm10H 0
# let's decode target for every 2-byte aligned offset in text section (0x00d00000..0x01800000)
hits = []
for pc in range(0x00e00000, 0x01800000, 2):
    hw1 = data[pc] | (data[pc+1] << 8)
    if (hw1 & 0xf800) == 0xf000:
        hw2 = data[pc+2] | (data[pc+3] << 8)
        # blx or bl
        if (hw2 & 0xd000) == 0xc000: # blx: bit 12 is 0, bit 14 is 1, bit 15 is 1
            s = (hw1 >> 10) & 1
            imm10 = hw1 & 0x3ff
            j1 = (hw2 >> 13) & 1
            j2 = (hw2 >> 11) & 1
            imm10h = (hw2 >> 1) & 0x7ff if (hw2 & 0x1000) else (hw2 & 0x7ff) # for blx bit 0 is 0
            i1 = ~(j1 ^ s) & 1
            i2 = ~(j2 ^ s) & 1
            imm32 = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm10h << 1)
            if s:
                imm32 -= (1 << 25)
            # For BLX to ARM: PC is (pc + 4) & ~3
            dest = ((pc + 4) & ~3) + imm32 if not (hw2 & 0x1000) else (pc + 4) + imm32
            if dest == target:
                hits.append(pc)

print(f"Found {len(hits)} calls to 0x{target:08x}:")
for h in hits:
    print(f"  0x{h:08x}")

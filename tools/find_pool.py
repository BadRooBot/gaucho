import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x00c74a38
print(f"Scanning for pc-relative loads to 0x{target:08x}...")
# Thumb LDR Rt, [PC, #imm8*4]
# 0100 1ttt imm8
for i in range(0, len(data)-2, 2):
    hw = struct.unpack('<H', data[i:i+2])[0]
    if (hw & 0xf800) == 0x4800:
        imm8 = hw & 0xff
        pc = (i + 4) & ~3
        dest = pc + (imm8 << 2)
        if dest == target:
            print(f'Thumb LDR at 0x{i:08x} loads 0x{dest:08x}')


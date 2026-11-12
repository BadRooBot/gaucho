import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x00f6df08
print(f"Scanning for 16-bit branches to 0x{target:08x}...")
for i in range(0x00f6dd90, 0x00f6e100, 2):
    hw = struct.unpack('<H', data[i:i+2])[0]
    # B<cond>: 1101 cond imm8
    if (hw & 0xf000) == 0xd000 and (hw & 0x0e00) != 0x0e00:
        imm8 = hw & 0xff
        if imm8 & 0x80: imm8 -= 0x100
        dest = (i + 4 + (imm8 << 1)) & 0xffffffff
        if abs(dest - target) <= 8:
            print(f'16-bit B<cond> at 0x{i:08x} -> 0x{dest:08x}')
    # B: 1110 0 imm11
    if (hw & 0xf800) == 0xe000:
        imm11 = hw & 0x7ff
        if imm11 & 0x400: imm11 -= 0x800
        dest = (i + 4 + (imm11 << 1)) & 0xffffffff
        if abs(dest - target) <= 8:
            print(f'16-bit B at 0x{i:08x} -> 0x{dest:08x}')


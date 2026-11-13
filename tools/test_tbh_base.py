import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

tbh_pc = 0x00f6de36  # tbh is at 0xf6de32 -> pc+4 = 0xf6de36

for base in [0x00f6de38, 0x00f6de3a, 0x00f6de3c, 0x00f6de3e, 0x00f6de40, 0x00f6de42]:
    print(f"\nTesting base 0x{base:08x}:")
    for i in range(10):
        h = struct.unpack('<H', data[base + i*2 : base + (i+1)*2])[0]
        target = tbh_pc + (h * 2)
        print(f"  entry {i} (action {0x4a+i}): h=0x{h:04x} -> target=0x{target:08x}")


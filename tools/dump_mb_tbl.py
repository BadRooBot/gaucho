import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

base_pc = 0x00f6de36 # pc for tbh
base_r1 = base_pc + 0x10 # 0x00f6de46 or 0x00f6de42?
# In ARMv7 thumb:
# 0x00f6de2e: addw r1, pc, #0x10 -> pc is 0x00f6de2e + 4 = 0x00f6de32. +0x10 = 0x00f6de42.
base_tbl = 0x00f6de42
print(f"Table at 0x{base_tbl:08x}:")
for i in range(0x5c):
    action = 0x4a + i # 74 + i
    h = struct.unpack('<H', data[base_tbl + i*2 : base_tbl + (i+1)*2])[0]
    target = base_tbl + (h * 2)
    if action in [74, 76, 78, 86, 97, 132]:
        print(f"Action {action} (0x{action:02x}): half=0x{h:04x} -> target=0x{target:08x}")


import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's verify base_tbl address
# 0x00f6de2e: addw r1, pc, #0x10 -> in thumb, pc is instruction address + 4
# Instruction at 0x00f6de2e: pc = 0x00f6de32. 0x00f6de32 + 0x10 = 0x00f6de42.
# But wait! In tbh [r1, r2, lsl #1], is base r1 or pc? It is [r1, r2, lsl #1] where r1 is base!
base_tbl = 0x00f6de42
for i in range(0x5c):
    action = 0x4a + i
    h = struct.unpack('<H', data[base_tbl + i*2 : base_tbl + (i+1)*2])[0]
    target = base_tbl + (h * 2)
    print(f"Action {action:3d} (0x{action:02x}): half=0x{h:04x} -> target=0x{target:08x}")


with open('work_mod/base_decoded/lib/armeabi-v7a/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

import struct

# Let's inspect the target of blx #0xceb1d4 and the literal pool at 0x15a377c, 0x15a377e
# 0x15a377c: ldr r1, [pc, #0xcc] -> pc is 0x15a3780 -> addr = 0x15a3780 + 0xcc = 0x15a384c
# 0x15a377e: ldr r3, [pc, #0xd0] -> pc is 0x15a3782 -> addr = 0x15a3782 + 0xd0 = 0x15a3852

off1 = 0x15a3780 + 0xcc
off2 = 0x15a3782 + 0xd0
val1 = struct.unpack('<I', data[off1:off1+4])[0]
val2 = struct.unpack('<I', data[off2:off2+4])[0]
print(f"val1: 0x{val1:08x}, target: 0x{off1 + val1:08x}")
print(f"val2: 0x{val2:08x}, target: 0x{off2 + val2:08x}")


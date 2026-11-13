import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

tbl_addr = 0x00f6de40
tbh_pc = 0x00f6de36

for i in range(92):
    action = 0x4a + i
    h = struct.unpack('<H', data[tbl_addr + i*2 : tbl_addr + (i+1)*2])[0]
    target = tbh_pc + (h * 2)
    print(f"Action {action:3d} (0x{action:02x}) -> target=0x{target:08x} (h=0x{h:04x})")


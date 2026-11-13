import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

tbh_pc = 0x00f6de36
tbl_base = 0x00f6de42

for r2 in range(92):
    offset = struct.unpack('<H', data[tbl_base + r2*2 : tbl_base + (r2+1)*2])[0]
    target = tbh_pc + 2 * offset
    action = 74 + r2
    print(f'Action {action:3d} (0x{action:02x}, r2={r2:2d}): offset=0x{offset:04x} -> target=0x{target:08x}')

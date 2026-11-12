import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

base_tbl = 0x00f6de42
for i in range(0x5c):
    action = 0x4a + i
    h = struct.unpack('<H', data[base_tbl + i*2 : base_tbl + (i+1)*2])[0]
    target = base_tbl + (h * 2)
    if 0x00f6df00 <= target <= 0x00f6df10:
        print(f"Action {action} (0x{action:02x}) -> target=0x{target:08x}")


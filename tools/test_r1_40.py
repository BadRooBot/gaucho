import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

r1 = 0x00f6de40
tbh_pc = 0x00f6de36

print(f"Table at r1 = 0x{r1:08x}:")
for i in range(0x5c):
    action = 0x4a + i
    h = struct.unpack('<H', data[r1 + i*2 : r1 + (i+1)*2])[0]
    target = tbh_pc + (h * 2)
    if 0x00f6df00 <= target <= 0x00f6df20:
        print(f"--> FOUND! Action {action} (0x{action:02x}) -> target=0x{target:08x}")
    elif action in [74, 75, 76, 78, 86, 97]:
        print(f"Action {action} (0x{action:02x}) -> target=0x{target:08x}")


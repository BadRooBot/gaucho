import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x02ef4580
# References to target in literal pools
for i in range(0, len(data), 4):
    v = struct.unpack('<I', data[i:i+4])[0]
    if v == target:
        print(f"Literal at 0x{i:08x}: 0x{v:08x}")

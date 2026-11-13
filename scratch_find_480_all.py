import struct, capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# movw rx, #0x480: 0xf240, 0x4080 | (rx << 8)
# Let's search across the entire binary!
for rx in range(13):
    pat = struct.pack('<HH', 0xf240, 0x4080 | (rx << 8))
    idx = 0
    while True:
        idx = data.find(pat, idx)
        if idx == -1: break
        print(f'movw r{rx}, #0x480 at 0x{idx:08x}')
        idx += 2

# Also in ARM mode:
# mov rx, #0x480 -> e3a0x...
# In ARMv7: movw rx, #0x480 -> e300x480
for rx in range(13):
    pat = struct.pack('<I', 0xe3000480 | (rx << 12))
    idx = 0
    while True:
        idx = data.find(pat, idx)
        if idx == -1: break
        print(f'ARM movw r{rx}, #0x480 at 0x{idx:08x}')
        idx += 4

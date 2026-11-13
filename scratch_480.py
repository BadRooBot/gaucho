import struct, capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

# In Thumb: movw rx, #0x480
# 0x480: imm4 = 0, i = 0, imm3 = 4, imm8 = 0x80
# high word: 0xf240
# low word: 0x4080 | (rd << 8)
for rd in range(13):
    pat = struct.pack('<HH', 0xf240, 0x4080 | (rd << 8))
    idx = 0
    while True:
        idx = data.find(pat, idx)
        if idx == -1: break
        print(f'movw r{rd}, #0x480 at 0x{idx:08x}')
        idx += 2

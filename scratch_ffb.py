import struct, capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# movw rd, #0xffb in Thumb:
# f240 7d fb (rd can be r0..r12)
# f640 7d fb etc.
# In Thumb: movw rd, #imm16: 1111 0 i 10 0 1 0 0 imm4 0 imm3 rd imm8
# For 0xffb: imm4 = 0, i = 0, imm3 = 7, imm8 = 0xfb
# high word: 1111 0 0 10 0 1 0 0 0000 = 0xf240
# low word: 0 111 rd 1111 1011 = 0x70fb | (rd << 8)
for rd in range(13):
    pat = struct.pack('<HH', 0xf240, 0x70fb | (rd << 8))
    idx = 0
    while True:
        idx = data.find(pat, idx)
        if idx == -1: break
        print(f'movw r{rd}, #0xffb at 0x{idx:08x}')
        idx += 2


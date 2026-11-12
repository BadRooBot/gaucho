import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Search for movw r0, #0x483 (in thumb: f240 4083)
target_seq = b'\x40\xf2\x83\x40' # movw r0, #0x483 in thumb
idx = 0
while True:
    idx = data.find(target_seq, idx)
    if idx == -1: break
    print(f'Found movw r0, #0x483 at 0x{idx:08x}')
    idx += 4


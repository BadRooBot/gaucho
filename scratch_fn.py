import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Find the function prologue before 0x0160cbb0
for addr in range(0x0160cbb0, 0x0160c000, -2):
    b0 = data[addr]
    b1 = data[addr+1]
    if b1 == 0xb5: # PUSH {..., LR}
        print(f'Function starts at 0x{addr:08x}')
        break


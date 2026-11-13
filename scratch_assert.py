import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x25307c3
# In Thumb, PC-relative offset: (target - (pc))
# Let's search all 4-byte words
for i in range(0, len(data)-4, 4):
    val = struct.unpack('<I', data[i:i+4])[0]
    # PC-relative in Thumb: pc is i + 4
    if (i + 4 + val) & 0xffffffff == 0x253079a: # start of string "msg.Create..."
        print(f'PC-rel reference at 0x{i:08x}')
    elif (i + val) & 0xffffffff == 0x253079a:
        print(f'PC-rel (no+4) at 0x{i:08x}')
    elif val == 0x253079a:
        print(f'Absolute reference at 0x{i:08x}')


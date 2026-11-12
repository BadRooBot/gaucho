with open('work_mod/base_decoded/lib/armeabi-v7a/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

import struct

tbh_pc = 0x011f6f44
tbh_table = tbh_pc
print("Jump table from 0x11f6f44:")
for i in range(24):
    half = struct.unpack('<H', data[tbh_table + i*2 : tbh_table + (i+1)*2])[0]
    target = tbh_pc + half * 2
    print(f"ctrl {1000+i} (index {i}): half=0x{half:04x} -> target=0x{target:08x}")


import struct, capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x02ef4580
print(f'Scanning for references to s_nMaxPrgValue (0x{target:08x})...')

# In ARM/Thumb, references to .bss variables are loaded via PC-relative pools:
# ldr r0, [pc, #offset] -> r0 = target_offset_or_addr
# add r0, pc (if relative)
# Let's search for the value in all 4-byte words
for i in range(0, len(data)-4, 4):
    val = struct.unpack('<I', data[i:i+4])[0]
    if val == target:
        print(f'Absolute ref in pool at 0x{i:08x}')
    elif (i + val) & 0xffffffff == target:
        print(f'Relative ref (val + addr = target) in pool at 0x{i:08x}')
    elif (i + 4 + val) & 0xffffffff == target:
        print(f'Thumb PC-rel ref (val + addr + 4 = target) in pool at 0x{i:08x}')


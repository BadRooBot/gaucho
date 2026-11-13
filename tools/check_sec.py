import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

e_shoff = struct.unpack('<I', data[0x20:0x24])[0]
e_shentsize = struct.unpack('<H', data[0x2e:0x30])[0]
e_shnum = struct.unpack('<H', data[0x30:0x32])[0]
e_shstrndx = struct.unpack('<H', data[0x32:0x34])[0]
shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
shstr_off = struct.unpack('<I', shstr_hdr[16:20])[0]

for i in range(e_shnum):
    sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
    name_idx = struct.unpack('<I', sh[0:4])[0]
    name = data[shstr_off + name_idx:].split(b'\0')[0].decode('latin-1')
    sh_addr = struct.unpack('<I', sh[12:16])[0]
    sh_size = struct.unpack('<I', sh[20:24])[0]
    if sh_addr <= 0xcea040 < sh_addr + sh_size:
        print(f"0xcea040 is in {name} (0x{sh_addr:x} .. 0x{sh_addr+sh_size:x})")


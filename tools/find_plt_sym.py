import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

e_shoff = struct.unpack('<I', data[0x20:0x24])[0]
e_shentsize = struct.unpack('<H', data[0x2e:0x30])[0]
e_shnum = struct.unpack('<H', data[0x30:0x32])[0]
e_shstrndx = struct.unpack('<H', data[0x32:0x34])[0]
shstr_hdr = data[e_shoff + e_shstrndx*e_shentsize : e_shoff + (e_shstrndx+1)*e_shentsize]
shstr_off = struct.unpack('<I', shstr_hdr[16:20])[0]
sections = {}
for i in range(e_shnum):
    sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
    name_idx = struct.unpack('<I', sh[0:4])[0]
    name = data[shstr_off + name_idx:].split(b'\0')[0].decode('latin-1')
    sections[name] = sh

rel_sh = sections['.rel.plt']
sym_sh = sections['.dynsym']
str_sh = sections['.dynstr']
plt_sh = sections['.plt']

rel_off = struct.unpack('<I', rel_sh[16:20])[0]
sym_off = struct.unpack('<I', sym_sh[16:20])[0]
str_off = struct.unpack('<I', str_sh[16:20])[0]
str_sz = struct.unpack('<I', str_sh[20:24])[0]
str_data = data[str_off : str_off + str_sz]
plt_addr = struct.unpack('<I', plt_sh[12:16])[0]

plt_stub = 0xcea040
# plt stub calculation:
idx = (plt_stub - (plt_addr + 0x14)) // 12
print(f"PLT stub 0x{plt_stub:x} -> index {idx}")

r_offset, r_info = struct.unpack('<II', data[rel_off + idx*8 : rel_off + (idx+1)*8])
sym_idx = r_info >> 8
sym = data[sym_off + sym_idx*16 : sym_off + (sym_idx+1)*16]
st_name = struct.unpack('<I', sym[0:4])[0]
end = str_data.find(b'\0', st_name)
sname = str_data[st_name:end].decode('latin-1')
print(f"Symbol for 0x{plt_stub:x}: {sname} (GOT: 0x{r_offset:x})")


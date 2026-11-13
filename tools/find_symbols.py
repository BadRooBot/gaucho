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
sym_sh = sections['.dynsym']
str_sh = sections['.dynstr']
sym_off = struct.unpack('<I', sym_sh[16:20])[0]
str_off = struct.unpack('<I', str_sh[16:20])[0]
str_sz = struct.unpack('<I', str_sh[20:24])[0]
str_data = data[str_off : str_off + str_sz]

target = 0x02db85a0
for sec_name in ['.rel.dyn', '.rel.plt']:
    if sec_name in sections:
        rel_sh = sections[sec_name]
        rel_off = struct.unpack('<I', rel_sh[16:20])[0]
        rel_sz = struct.unpack('<I', rel_sh[20:24])[0]
        for i in range(rel_sz // 8):
            r_offset, r_info = struct.unpack('<II', data[rel_off + i*8 : rel_off + (i+1)*8])
            if abs(r_offset - target) < 0x40:
                sym_idx = r_info >> 8
                sym = data[sym_off + sym_idx*16 : sym_off + (sym_idx+1)*16]
                st_name = struct.unpack('<I', sym[0:4])[0]
                end = str_data.find(b'\0', st_name)
                sname = str_data[st_name:end].decode('latin-1')
                print(f"{sec_name} offset 0x{r_offset:x} (diff {r_offset - target}): {sname}")

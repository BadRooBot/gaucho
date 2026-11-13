import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's decode the 3 instructions at 0x00cea040
addr = 0x00cea040
w0, w1, w2 = struct.unpack('<III', data[addr:addr+12])
imm0 = w0 & 0xff
rot0 = ((w0 >> 8) & 0xf) * 2
val0 = ((imm0 >> rot0) | (imm0 << (32 - rot0))) & 0xffffffff if rot0 else imm0

imm1 = w1 & 0xff
rot1 = ((w1 >> 8) & 0xf) * 2
val1 = ((imm1 >> rot1) | (imm1 << (32 - rot1))) & 0xffffffff if rot1 else imm1

imm2 = w2 & 0xfff
got_addr = (addr + 8 + val0 + val1 + imm2) & 0xffffffff
print(f'GOT target: 0x{got_addr:08x}')

# Find in .rel.plt
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

rel = sections.get('.rel.plt')
dynsym = sections.get('.dynsym')
dynstr = sections.get('.dynstr')

r_off = struct.unpack('<I', rel[16:20])[0]
r_sz = struct.unpack('<I', rel[20:24])[0]
s_off = struct.unpack('<I', dynsym[16:20])[0]
str_off = struct.unpack('<I', dynstr[16:20])[0]

for i in range(r_sz // 8):
    entry = data[r_off + i*8 : r_off + (i+1)*8]
    r_offset, r_info = struct.unpack('<II', entry)
    if r_offset == got_addr:
        sym_idx = r_info >> 8
        sym_entry = data[s_off + sym_idx*16 : s_off + (sym_idx+1)*16]
        st_name = struct.unpack('<I', sym_entry[0:4])[0]
        name = data[str_off + st_name:].split(b'\0')[0].decode('latin-1')
        print(f'Symbol: {name}')
        break

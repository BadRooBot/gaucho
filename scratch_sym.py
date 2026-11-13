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

sh_dynsym = sections['.dynsym']
sh_dynstr = sections['.dynstr']
dynsym_off = struct.unpack('<I', sh_dynsym[16:20])[0]
dynstr_off = struct.unpack('<I', sh_dynstr[16:20])[0]

entry = data[0x00131930 : 0x00131940]
st_name, st_value, st_size = struct.unpack('<III', entry[:12])
name = data[dynstr_off + st_name:].split(b'\0')[0].decode('latin-1')
print(f'Symbol at 0x00131930: name="{name}" st_value=0x{st_value:08x} st_size={st_size}')

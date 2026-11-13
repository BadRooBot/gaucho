import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's find symbol index of _ZN11CMyShellDlg18ProcessLoginStatusEv
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
dynsym_off = struct.unpack('<I', sh_dynsym[16:20])[0]
dynsym_sz = struct.unpack('<I', sh_dynsym[20:24])[0]

sym_idx = (0x00131930 - dynsym_off) // 16
print(f'Symbol index: {sym_idx}')

# Scan .rel.dyn and .rel.plt for references to sym_idx
for sec_name in ['.rel.dyn', '.rel.plt']:
    sh = sections[sec_name]
    r_off = struct.unpack('<I', sh[16:20])[0]
    r_sz = struct.unpack('<I', sh[20:24])[0]
    for i in range(r_sz // 8):
        offset, info = struct.unpack('<II', data[r_off + i*8 : r_off + (i+1)*8])
        if (info >> 8) == sym_idx:
            print(f'{sec_name} ref at offset 0x{offset:08x}')

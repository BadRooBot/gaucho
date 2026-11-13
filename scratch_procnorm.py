import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

idx = data.find(b'_ZN11CMyShellDlg13ProcessNormalEv\x00')

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
dynsym_sz = struct.unpack('<I', sh_dynsym[20:24])[0]
dynstr_off = struct.unpack('<I', sh_dynstr[16:20])[0]

target_off = idx - dynstr_off
for i in range(dynsym_sz // 16):
    sym = data[dynsym_off + i*16 : dynsym_off + (i+1)*16]
    st_name = struct.unpack('<I', sym[0:4])[0]
    if st_name == target_off:
        st_val = struct.unpack('<I', sym[4:8])[0]
        st_sz = struct.unpack('<I', sym[8:12])[0]
        print(f'_ZN11CMyShellDlg13ProcessNormalEv at 0x{st_val:08x} (sz {st_sz})')

import struct

with open('work_mod/base_decoded/lib/armeabi-v7a/libCQ2ClientEn.so', 'rb') as f:
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

sh = sections['.dynsym']
str_sh = sections['.dynstr']
sym_off = struct.unpack('<I', sh[16:20])[0]
sym_sz = struct.unpack('<I', sh[20:24])[0]
str_off = struct.unpack('<I', str_sh[16:20])[0]
str_sz = struct.unpack('<I', str_sh[20:24])[0]
str_data = data[str_off : str_off + str_sz]

# Find all offsets in str_data where "CNewFunctionOpenMgr" appears
target_offsets = {}
idx = 0
while True:
    idx = str_data.find(b'CNewFunctionOpenMgr', idx)
    if idx == -1: break
    # Find start of string (preceding null byte)
    start = str_data.rfind(b'\0', 0, idx)
    start = 0 if start == -1 else start + 1
    end = str_data.find(b'\0', idx)
    name = str_data[start:end].decode('latin-1')
    target_offsets[start] = name
    idx = end + 1

print(f"Found {len(target_offsets)} matching strings in .dynstr")

# Now check .dynsym
for i in range(sym_sz // 16):
    sym = data[sym_off + i*16 : sym_off + (i+1)*16]
    st_name = struct.unpack('<I', sym[0:4])[0]
    if st_name in target_offsets:
        st_value = struct.unpack('<I', sym[4:8])[0]
        st_size = struct.unpack('<I', sym[8:12])[0]
        print(f"0x{st_value:08x} (sz {st_size:4d}) {target_offsets[st_name]}")

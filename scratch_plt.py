import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

target = 0x02e00ad4
# PLT stubs look like:
# add ip, pc, ...
# add ip, ip, ...
# ldr pc, [ip, #offset]!
# Let's search .plt section
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

plt = sections['.plt']
plt_off = struct.unpack('<I', plt[16:20])[0]
plt_sz = struct.unpack('<I', plt[20:24])[0]

# In ARM PLT:
# each stub is 12 bytes:
# add ip, pc, ...
# add ip, ip, ...
# ldr pc, [ip, #imm]!
# Let's find which stub resolves to 0x02e00ad4
for addr in range(plt_off + 20, plt_off + plt_sz, 12):
    # pc is addr + 8
    # Let's decode the 3 instructions
    w0, w1, w2 = struct.unpack('<III', data[addr:addr+12])
    if (w0 & 0xfffff000) == 0xe28fc000 and (w1 & 0xfffff000) == 0xe28cc000 and (w2 & 0xfffff000) == 0xe5bcf000:
        imm0 = (w0 & 0xff)
        rot0 = ((w0 >> 8) & 0xf) * 2
        val0 = ((imm0 >> rot0) | (imm0 << (32 - rot0))) & 0xffffffff if rot0 else imm0
        imm1 = (w1 & 0xff)
        rot1 = ((w1 >> 8) & 0xf) * 2
        val1 = ((imm1 >> rot1) | (imm1 << (32 - rot1))) & 0xffffffff if rot1 else imm1
        imm2 = w2 & 0xfff
        calc = (addr + 8 + val0 + val1 + imm2) & 0xffffffff
        if calc == target:
            print(f'PLT stub for ProcessLoginStatus at 0x{addr:08x}')

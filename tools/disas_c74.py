import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
# Let's check ARM or Thumb mode around 0x00c74a00
for mode, m_name in [(capstone.CS_MODE_ARM, 'ARM'), (capstone.CS_MODE_THUMB, 'Thumb')]:
    print(f'=== {m_name} mode ===')
    cs_m = capstone.Cs(capstone.CS_ARCH_ARM, mode)
    start = 0x00c74a10
    code = data[start:start+0x50]
    for ins in cs_m.disasm(code, start):
        print(f'0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str}')


import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
start = 0x00f6df08
code = data[start:start+0xc0]
for ins in cs.disasm(code, start):
    print(f'0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str}')


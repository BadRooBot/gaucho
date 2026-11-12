import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
for addr in [0xce7670, 0xd4f1c4, 0xd4f1dc]:
    print(f'=== 0x{addr:08x} ===')
    code = data[addr:addr+16]
    for ins in cs.disasm(code, addr):
        print(f'0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str}')


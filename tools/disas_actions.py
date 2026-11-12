import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

print("=== Action 251 (0x00f6f2bc) ===")
start = 0x00f6f2bc
code = data[start:start+0x80]
for ins in cs.disasm(code, start):
    print(f'0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str}')

print("=== Action 471 (0x00f6f25a) ===")
start = 0x00f6f25a
code = data[start:start+0x80]
for ins in cs.disasm(code, start):
    print(f'0x{ins.address:08x}:  {ins.mnemonic:<8} {ins.op_str}')


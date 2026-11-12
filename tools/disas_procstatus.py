import capstone

with open('work_mod/base_decoded/lib/armeabi-v7a/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

addr = 0x015a3614
size = 576
code = data[addr : addr + size]
for ins in md.disasm(code, addr):
    print(f'0x{ins.address:08x}:  {ins.mnemonic:8s} {ins.op_str}')


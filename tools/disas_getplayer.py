import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

start = 0x0105bfc0
length = 180
chunk = data[start:start+length]

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
for insn in md.disasm(chunk, start):
    print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")


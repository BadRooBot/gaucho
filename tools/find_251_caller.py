import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's find branches to 0x00f6f2bc
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
chunk = data[0x00f6c000:0x00f72000]
start = 0x00f6c000

for insn in md.disasm(chunk, start):
    if insn.mnemonic.startswith('b') and '0xf6f2bc' in insn.op_str:
        print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")


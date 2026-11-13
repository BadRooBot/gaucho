import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Action 74 handler in CMsgMBAction::Process
# Let's disassemble from 0x00f6de00 to 0x00f6e020
start = 0x00f6de00
length = 0x220
chunk = data[start:start+length]

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
for insn in md.disasm(chunk, start):
    print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

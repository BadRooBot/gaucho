import capstone, struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's check how action 408 (0x198) is handled in CMsgMBAction::Process
# We can search for 408 / 0x198 in CMsgMBAction::Process (0x00f6c000..0x00f72000)
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
chunk = data[0x00f6c000:0x00f72000]
start = 0x00f6c000

for insn in md.disasm(chunk, start):
    if '0x198' in insn.op_str or '408' in insn.op_str:
        print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")


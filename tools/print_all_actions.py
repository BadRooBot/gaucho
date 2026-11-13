import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's search where [r4, #0x44] or action comparisons occur in CMsgMBAction::Process
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
chunk = data[0x00f6d000:0x00f72000]
start = 0x00f6d000

for insn in md.disasm(chunk, start):
    if insn.mnemonic.startswith('cmp') or insn.mnemonic.startswith('sub'):
        if any(f"#{val}" in insn.op_str for val in [408, 0x198, 251, 0xfb, 471, 0x1d7]):
            print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

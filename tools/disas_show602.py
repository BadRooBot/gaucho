import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

locations = [0x012b0ea0, 0x01408dd0, 0x0156eab0, 0x01612b10]
for loc in locations:
    print(f"\n--- Location 0x{loc:08x} ---")
    chunk = data[loc:loc+0x40]
    for insn in md.disasm(chunk, loc):
        print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")


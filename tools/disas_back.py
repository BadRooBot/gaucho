import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

# Try different start offsets before 0xf6df08 so that an instruction boundary lands on 0xf6df08
for start in range(0xf6dee0, 0xf6df08, 2):
    insns = list(md.disasm(data[start:0xf6df20], start))
    if any(insn.address == 0xf6df08 for insn in insns):
        print(f"Aligned start 0x{start:x}:")
        for insn in insns:
            if insn.address <= 0xf6df20:
                print(f"  0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")
        break

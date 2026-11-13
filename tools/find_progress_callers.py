import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# In thumb: blx #0xd56190 or bl #0x0125ded4
# Let's search all bl/blx calls that target 0xd56190 or 0x0125ded4
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

chunk = data[0x00f00000:0x01800000]
start = 0x00f00000

for insn in md.disasm(chunk, start):
    if insn.mnemonic in ('bl', 'blx'):
        if 'd56190' in insn.op_str or '125ded4' in insn.op_str or '125ded5' in insn.op_str:
            # print preceding 4 instructions
            prev_chunk = data[insn.address - 16 : insn.address]
            prev_insns = list(md.disasm(prev_chunk, insn.address - 16))
            print(f"Call at 0x{insn.address:08x}:")
            for pi in prev_insns:
                print(f"  0x{pi.address:08x}: {pi.mnemonic} {pi.op_str}")
            print(f"  0x{insn.address:08x}: {insn.mnemonic} {insn.op_str}")

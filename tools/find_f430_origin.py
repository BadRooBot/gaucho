import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's find branches or jumps leading to 0xf6f430 or earlier
# Let's disassemble backwards from 0xf6f430 to 0xf6f3b0
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

# Let's search who branches to 0x00f6f430 or nearby
for addr in range(0xf6d000, 0xf6f430, 2):
    # disassemble one instruction
    insns = list(md.disasm(data[addr:addr+4], addr))
    if insns:
        insn = insns[0]
        if insn.mnemonic.startswith('b') and ('0xf6f4' in insn.op_str or '0xf6f3' in insn.op_str):
            print(f"Branch at 0x{insn.address:08x}: {insn.mnemonic} {insn.op_str}")

# Also disassemble linearly from 0xf6f3b0 to 0xf6f430
print("\nLinear disassembly 0xf6f3b0..0xf6f430:")
for insn in md.disasm(data[0xf6f3b0:0xf6f430], 0xf6f3b0):
    print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")


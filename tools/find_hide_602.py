import capstone, struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's find callers of 0x0150406b in libCQ2ClientEn.so
# In Thumb-2: bl or blx to 0x0150406b
# bl target = pc + offset
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

chunk = data[0x00f00000:0x01800000]
start = 0x00f00000

for insn in md.disasm(chunk, start):
    if insn.mnemonic in ('bl', 'blx') and ('0x150406a' in insn.op_str or '0x150406b' in insn.op_str or '0xd44970' in insn.op_str):
        # Disassemble 5 instructions prior to check arguments (r0 = this, r1 = winId, r2 = bool)
        prev_chunk = data[insn.address - 20 : insn.address]
        prev_insns = list(md.disasm(prev_chunk, insn.address - 20))
        if any('0x25a' in pi.op_str or '602' in pi.op_str for pi in prev_insns):
            print(f"Call to HideMyWindow(602) at 0x{insn.address:08x}:")
            for pi in prev_insns:
                print(f"   0x{pi.address:08x}: {pi.mnemonic} {pi.op_str}")
            print(f"   0x{insn.address:08x}: {insn.mnemonic} {insn.op_str}")


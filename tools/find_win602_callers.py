import capstone, struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

show_stubs = [0x00d4176c, 0x00d42a14, 0x00d7ea50]
hide_stubs = [0x00d44970]

# Search code
chunk = data[0x00f00000:0x01800000]
start_addr = 0x00f00000

print("Scanning for ShowMyWindow(602) and HideMyWindow(602)...")
for insn in md.disasm(chunk, start_addr):
    if insn.mnemonic == 'blx':
        target = 0
        try:
            target = int(insn.op_str.replace('#', ''), 16)
        except:
            pass
        if target in show_stubs:
            # check previous instructions for 0x25a (602)
            # look back 16 bytes
            prev_chunk = data[insn.address - 16 : insn.address]
            prev_insns = list(md.disasm(prev_chunk, insn.address - 16))
            if any('0x25a' in pi.op_str for pi in prev_insns):
                print(f"Show 602 at 0x{insn.address:08x}:")
                for pi in prev_insns[-3:]:
                    print(f"   0x{pi.address:08x}: {pi.mnemonic} {pi.op_str}")
                print(f"   0x{insn.address:08x}: {insn.mnemonic} {insn.op_str}")
        elif target in hide_stubs:
            prev_chunk = data[insn.address - 16 : insn.address]
            prev_insns = list(md.disasm(prev_chunk, insn.address - 16))
            if any('0x25a' in pi.op_str for pi in prev_insns):
                print(f"Hide 602 at 0x{insn.address:08x}:")
                for pi in prev_insns[-3:]:
                    print(f"   0x{pi.address:08x}: {pi.mnemonic} {pi.op_str}")
                print(f"   0x{insn.address:08x}: {insn.mnemonic} {insn.op_str}")


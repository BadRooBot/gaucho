import capstone, struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# At 0xf6de2e: addw r1, pc, #0x10 -> pc is 0xf6de2e + 4 = 0xf6de32 -> +0x10 = 0xf6de42? Or in thumb: pc is (addr + 4) & ~1 = 0xf6de32.
# Let's check tbh base:
# In Thumb-2:
# 0xf6de2e: addw r1, pc, #0x10
# pc for 0xf6de2e is 0xf6de2e + 4 = 0xf6de32.
# r1 = 0xf6de32 + 0x10 = 0xf6de42. Wait, 0xf6de2e is 4-byte instruction:
# Let's inspect raw bytes from 0xf6de20 to 0xf6df20.
chunk = data[0xf6de20:0xf6df20]
print("raw bytes around jump table:")
print(chunk[:40].hex())

# Let's disassemble from 0xf6deec to 0xf6dfd0
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
for insn in md.disasm(data[0xf6def0:0xf6dfd0], 0xf6def0):
    print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

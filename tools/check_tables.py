import struct, capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's inspect what switches are at 0xf6d416 and 0xf6d538
# Disassemble instructions leading to 0xf6d416
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

print("--- At 0xf6d400: ---")
for insn in md.disasm(data[0xf6d400:0xf6d41a], 0xf6d400):
    print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

# Table at 0xf6d416: tbh [pc, r1, lsl #1]
# In Thumb: PC for tbh at 0xf6d416 is (0xf6d416 + 4) = 0xf6d41a
# Base is 0xf6d41a
for i in range(50):
    h = struct.unpack('<H', data[0xf6d41a + i*2 : 0xf6d41a + (i+1)*2])[0]
    target = 0xf6d41a + h * 2
    if 0xf6f200 <= target <= 0xf6f300:
        print(f"Match entry {i} in table 1: target=0x{target:x}")

print("\n--- At 0xf6d520: ---")
for insn in md.disasm(data[0xf6d520:0xf6d53c], 0xf6d520):
    print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

for i in range(50):
    h = struct.unpack('<H', data[0xf6d53c + i*2 : 0xf6d53c + (i+1)*2])[0]
    target = 0xf6d53c + h * 2
    if 0xf6f200 <= target <= 0xf6f300:
        print(f"Match entry {i} in table 2: target=0x{target:x}")


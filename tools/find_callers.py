import capstone, struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's search who branches to 0x00f6df08 (or nearby, like 0x00f6df00..0x00f6df10)
# or where 0x00f6df08 is in jump tables.
target_addr = 0x00f6df08

print("Scanning for branches to 0x00f6df08...")
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

# CMsgMBAction::Process is around 0x00f6d000 to 0x00f70000
chunk = data[0x00f6c000:0x00f72000]
start = 0x00f6c000

for insn in md.disasm(chunk, start):
    if insn.mnemonic.startswith('b') or insn.mnemonic.startswith('cb'):
        # check op_str
        if f"0x{target_addr:x}" in insn.op_str:
            print(f"Branch to target: 0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")
        elif "0xf6df" in insn.op_str:
            print(f"Branch near target: 0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

# Check all tbh / tbb in the region
print("\nChecking jump tables...")
for insn in md.disasm(chunk, start):
    if insn.mnemonic in ('tbh', 'tbb'):
        print(f"Table at 0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

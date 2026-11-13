import capstone, struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's inspect the tables at 0xf6d416, 0xf6d538, and around 0xf6de32
def check_tbh(pc_tbh, num_entries, base_reg_pc):
    print(f"\n--- Checking TBH at 0x{pc_tbh:08x} (base_pc=0x{base_reg_pc:08x}) ---")
    for i in range(num_entries):
        h = struct.unpack('<H', data[base_reg_pc + i*2 : base_reg_pc + (i+1)*2])[0]
        # In ARM Thumb, tbh target = (pc of tbh + 4) + h * 2
        target = (pc_tbh + 4) + h * 2
        if 0x00f6df00 <= target <= 0x00f6df20:
            print(f"MATCH entry {i}: target=0x{target:08x} (h=0x{h:x})")

# Let's check table at 0xf6d416: in tbh [pc, r1, lsl #1], base is pc+4 = 0xf6d41a
check_tbh(0xf6d416, 120, 0xf6d41a)
check_tbh(0xf6d538, 120, 0xf6d53c)

# And what was at 0xf6de2e / 0xf6de32?
# 0xf6de2e: addw r1, pc, #0x10 -> pc is 0xf6de2e + 4 = 0xf6de32. r1 = 0xf6de32 + 0x10 = 0xf6de42.
# 0xf6de32: tbh [r1, r2, lsl #1]
# For this tbh, target = (0xf6de32 + 4) + h * 2 = 0xf6de36 + h * 2? Or r1 + h * 2?
# The instruction tbh [r1, r2, lsl #1] calculates: PC = PC + (Halfwords[r1 + r2*2] * 2).
# Wait! In ARM Architecture Reference Manual:
# Branch target for TBH is: PC = PC + 2 * offset!
# where PC is the address of the TBH instruction plus 4!
# So PC = 0xf6de32 + 4 = 0xf6de36.
# Target = 0xf6de36 + (offset * 2).
# Let's check all entries with base 0xf6de42:
check_tbh(0xf6de32, 120, 0xf6de42)

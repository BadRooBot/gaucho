import capstone, struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Search for 0x480 (1152) and 0x400 (1024) in the code
# In Thumb-2:
# mov.w r0, #0x480 -> f44f 6090 or similar
# mov.w r1, #0x400 -> f44f 6180 or similar
# Let's search bytes where 0x480 or 0x400 is loaded or where 0x480 is passed to PostCmd

# In the summary:
# "CMsgMBAction::Process for Action 74 (0x00f6df08..0x00f6df10):
# mov.w r0, #0x480
# mov.w r1, #0x400 (1024)
# blx PostCmd(0x480, 0x400)
# Sends Action 75 (0x4b) to server.
# Gated by: CGamePlayerSet::GetPlayer(field 1, true) (0x00f6de12). If Field 1 == CHero::m_dwId, it proceeds."

# Let's disassemble exactly from 0x00f6df00 to 0x00f6dfa0
start = 0x00f6df00
length = 0xa0
md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
for insn in md.disasm(data[start:start+length], start):
    print(f"0x{insn.address:x}: {insn.mnemonic} {insn.op_str}")

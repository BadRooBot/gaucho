import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# For 0xce7670:
# pc = 0xce7670 + 8 = 0xce7678
# ip = pc + 0x2000000 = 0x2ce7678
# ip = ip + 0xe2000 = 0x2dc9678
# [ip, #0x138] = 0x2dc97b0
for name, addr in [('0xce7670', 0xce7670), ('0xd4f1c4', 0xd4f1c4), ('0xd4f1dc', 0xd4f1dc)]:
    # compute GOT address
    # In ARM PLT:
    # 0: add ip, pc, #...
    # 4: add ip, ip, #...
    # 8: ldr pc, [ip, #...]!
    pc = addr + 8
    w0 = struct.unpack('<I', data[addr:addr+4])[0]
    w1 = struct.unpack('<I', data[addr+4:addr+8])[0]
    w2 = struct.unpack('<I', data[addr+8:addr+12])[0]
    # let's just inspect bytes in data at GOT
    # or let's find relocations in ELF:
    print(f"{name}: bytes: {w0:08x} {w1:08x} {w2:08x}")


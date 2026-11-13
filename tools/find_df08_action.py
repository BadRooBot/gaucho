with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

raw = data[0xf6def0:0xf6df20]
print("Hex 0xf6def0..0xf6df20:")
print(raw.hex())
# Print each halfword
for o in range(0xf6def0, 0xf6df20, 2):
    hw = data[o] | (data[o+1] << 8)
    print(f"0x{o:06x}: 0x{hw:04x}")

with open("tools/libCQ2ClientEn.so", "rb") as f:
    data = f.read()

for target in [0x0285d6fe, 0x028c8bde, 0x02822ba6]:
    s = data[target:target+40].split(b"\x00")[0]
    print(f"0x{target:08x}: {s}")

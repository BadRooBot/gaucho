
with open('tools/libCQ2ClientEn.so', 'rb') as fp:
    elf = fp.read()

target = 0x0125e3c8
print('Searching callers of SetLoadingProgress (0x0125e3c8)...')
for i in range(0, len(elf) - 4, 2):
    hw1 = int.from_bytes(elf[i:i+2], 'little')
    if (hw1 & 0xF800) == 0xF000:
        hw2 = int.from_bytes(elf[i+2:i+4], 'little')
        if (hw2 & 0xD000) == 0xD000:
            s = (hw1 >> 10) & 1
            imm10 = hw1 & 0x3FF
            j1 = (hw2 >> 13) & 1
            j2 = (hw2 >> 11) & 1
            imm11 = hw2 & 0x7FF
            i1 = ~(j1 ^ s) & 1
            i2 = ~(j2 ^ s) & 1
            imm32 = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
            if imm32 & (1 << 24):
                imm32 -= (1 << 25)
            dest = i + 4 + imm32
            if dest == target:
                print(f'Caller at 0x{i:08x}')

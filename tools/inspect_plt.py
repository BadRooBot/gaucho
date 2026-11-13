with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's find PLT or relocation for 0xcea040
import struct

plt_entry = 0xcea040
# In ARM Thumb PLT:
# add ip, pc, ...
# ldr pc, [ip, ...]
print(f"Bytes at 0x{plt_entry:x}: {data[plt_entry:plt_entry+16].hex()}")

# Let's check decode_reloc.py or scan_plt.py
import subprocess
p = subprocess.run(['python', 'tools/decode_reloc.py', hex(plt_entry)], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)

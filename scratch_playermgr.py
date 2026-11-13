import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

idx = 0
while True:
    idx = data.find(b'CPlayerManager', idx)
    if idx == -1: break
    start = data.rfind(b'\0', 0, idx) + 1
    end = data.find(b'\0', idx)
    name = data[start:end].decode('latin-1', errors='ignore')
    if any(k in name for k in ['GetPlayer', 'Create', 'Add', 'SetHero', 'InitHero']):
        print(name)
    idx = end + 1


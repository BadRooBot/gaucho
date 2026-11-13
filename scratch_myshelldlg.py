import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

idx = 0
methods = []
while True:
    idx = data.find(b'_ZN11CMyShellDlg', idx)
    if idx == -1: break
    start = idx
    end = data.find(b'\0', idx)
    m = data[start:end].decode('latin-1')
    methods.append(m)
    idx = end + 1

for m in sorted(set(methods)):
    print(m)


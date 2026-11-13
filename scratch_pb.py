import struct

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's search for MsgMBAction in .dynstr or strings
idx = 0
while True:
    idx = data.find(b'MsgMBAction', idx)
    if idx == -1: break
    start = data.rfind(b'\0', 0, idx) + 1
    end = data.find(b'\0', idx)
    print(data[start:end].decode('latin-1', errors='ignore'))
    idx = end + 1

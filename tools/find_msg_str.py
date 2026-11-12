import capstone

with open('tools/libCQ2ClientEn.so', 'rb') as f:
    data = f.read()

# Let's find xrefs to "CMsgActionPB" in .dynstr or strings
str_idx = data.find(b'CMsgActionPB')
print('CMsgActionPB string at:', hex(str_idx) if str_idx != -1 else 'Not found')
str_mb = data.find(b'CMsgMBAction')
print('CMsgMBAction string at:', hex(str_mb) if str_mb != -1 else 'Not found')


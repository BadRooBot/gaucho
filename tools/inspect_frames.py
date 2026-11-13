import json

def parse_pb(raw):
    idx = 0
    fields = {}
    while idx < len(raw):
        byte = raw[idx]
        idx += 1
        wire = byte & 7
        tag = byte >> 3
        if wire == 0:
            val = 0
            shift = 0
            while True:
                b = raw[idx]
                idx += 1
                val |= (b & 0x7f) << shift
                if not (b & 0x80):
                    break
                shift += 7
            fields[tag] = val
        elif wire == 2:
            length = 0
            shift = 0
            while True:
                b = raw[idx]
                idx += 1
                length |= (b & 0x7f) << shift
                if not (b & 0x80):
                    break
                shift += 7
            data = raw[idx:idx+length]
            idx += length
            fields[tag] = data
        elif wire == 5:
            fields[tag] = raw[idx:idx+4]
            idx += 4
        elif wire == 1:
            fields[tag] = raw[idx:idx+8]
            idx += 8
        else:
            fields[tag] = f"unknown wire {wire}"
            break
    return fields

with open('data/login_template.json') as f:
    t = json.load(f)

for i in range(52, 59):
    f = t['frames'][i]
    raw = bytes.fromhex(f['hex'])
    ty = f['ty']
    pb = parse_pb(raw) if ty == 0x273e else {}
    print(f"Frame {i}: ty=0x{ty:04x} len={len(raw)} pb={pb}")

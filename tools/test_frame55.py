import json

def parse_pb(data):
    i = 0
    fields = {}
    while i < len(data):
        tag = data[i]
        i += 1
        fn = tag >> 3
        wt = tag & 7
        if wt == 0:
            val = 0
            shift = 0
            while i < len(data):
                b = data[i]
                i += 1
                val |= (b & 0x7f) << shift
                shift += 7
                if not (b & 0x80):
                    break
            fields[fn] = val
        elif wt == 2:
            l = data[i]
            i += 1
            fields[fn] = data[i:i+l]
            i += l
        else:
            break
    return fields

d = json.load(open('data/login_template.json'))
f55 = d['frames'][55]
raw = bytes.fromhex(f55['hex'])
parsed = parse_pb(raw)
print("Original Frame 55:")
print(f"  hex: {f55['hex']}")
print(f"  parsed: {parsed}")


import json

with open('data/login_template.json', 'r') as f:
    data = json.load(f)

frames = data['frames']
for i, f in enumerate(frames[:65]):
    ty = f['ty']
    raw = bytes.fromhex(f['hex'])
    extra = ''
    if ty == 0x27c3:
        # strings in talk packet
        s = ''
        cur = []
        for b in raw:
            if 32 <= b < 127:
                cur.append(chr(b))
            else:
                if len(cur) >= 3:
                    s += ''.join(cur) + ' '
                cur = []
        if len(cur) >= 3:
            s += ''.join(cur)
        extra = f' talk: {s}'
    elif ty == 0x273e:
        # action pb
        extra = ' action'
    print(f'[{i}] ty=0x{ty:04x} ({ty}) len={len(raw)}{extra}')

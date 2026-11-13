import json

with open('tools/captures/report_last.jsonl', 'r', encoding='utf-8') as f:
    count = 0
    for line in f:
        pkt = json.loads(line)
        src = pkt.get('src', '')
        dst = pkt.get('dst', '')
        if '8021' in src or '8021' in dst:
            ts = pkt.get('time')
            size = pkt.get('size')
            ty = pkt.get('type')
            name = pkt.get('name')
            hex_data = pkt.get('hex', '')[:40]
            strings = pkt.get('strings', [])
            print(f"{ts} {src} -> {dst} sz={size} ty={ty} name={name} s={strings[:3]} hex={hex_data}")
            count += 1
            if count >= 60:
                break

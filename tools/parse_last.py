import json

with open('tools/captures/report_last.jsonl', 'r') as f:
    for i, line in enumerate(f):
        pkt = json.loads(line)
        src = pkt.get('src', '')
        dst = pkt.get('dst', '')
        if ':8021' in src or ':8021' in dst:
            t = pkt.get('type')
            name = pkt.get('name')
            hex_data = pkt.get('hex', '')
            direction = 'S2C' if ':8021' in src else 'C2S'
            print(f"[{i}] {pkt['time']} {direction} sz={pkt['size']} type={t} name={name} hex={hex_data[:30]}")
            if i > 500: break


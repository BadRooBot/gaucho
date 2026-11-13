import json

with open('tools/captures/report_last.jsonl', 'r', encoding='utf-8') as f:
    count = 0
    for line in f:
        obj = json.loads(line)
        src = obj.get('src', '')
        dst = obj.get('dst', '')
        if '8021' in src or '8021' in dst:
            t = obj.get('type')
            t_str = f'0x{t:04x}' if isinstance(t, int) else str(t)
            name = obj.get('name', '')
            tm = obj.get('time', '')
            sz = obj.get('size', 0)
            print(f"{tm} {src} -> {dst} sz={sz:4d} type={t_str:6s} name={name}")
            count += 1
            if count >= 40:
                break

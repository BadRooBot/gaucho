import json

count = 0
with open('tools/captures/report_last.jsonl', 'r') as f:
    for line in f:
        pkt = json.loads(line)
        # Look for 0x273e (CMsgMBAction = 10046)
        ty = pkt.get('type')
        if ty == 10046 or ty == 0x273e:
            print(f"{pkt.get('time')} [{pkt.get('dir')}]: len={pkt.get('len')} data={pkt.get('summary', '')}")
            count += 1
            if count >= 30:
                break


import json

count = 0
with open('tools/captures/report_last.jsonl', 'r') as f:
    for line in f:
        pkt = json.loads(line)
        # check if 10046 or 0x273e
        ptype = pkt.get('packet_type') or pkt.get('id') or pkt.get('type')
        payload = pkt.get('payload', '')
        # if action 74 (604a in hex)
        if '604a' in payload.lower():
            print(pkt)
            count += 1
            if count > 10: break

import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()

print(s[s.find('            s_fake_vg["historial"].sort(key=lambda x: x.get("timestamp", ""))'):s.find('            s_fake_vg["historial"].sort(key=lambda x: x.get("timestamp", ""))')+1500])

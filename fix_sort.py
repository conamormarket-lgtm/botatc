import sys

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target1 = 'hist_total.sort(key=lambda x: x.get("timestamp", ""))'
rep1 = 'hist_total.sort(key=lambda x: str(x.get("timestamp", "")))'

target2 = 's_fake_vg["historial"].sort(key=lambda x: x.get("timestamp", ""))'
rep2 = 's_fake_vg["historial"].sort(key=lambda x: str(x.get("timestamp", "")))'

if target1 in text: text = text.replace(target1, rep1)
if target2 in text: text = text.replace(target2, rep2)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Replaced sort functions")

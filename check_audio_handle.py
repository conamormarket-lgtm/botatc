import re
with open("server.py", "r", encoding="utf-8") as f:
    s = f.read()

m = re.search(r'match_audio = re\.match', s)
if m:
    print(s[max(0, m.start()-500):m.end()+1500])
else:
    print("Not found input container in server.py")

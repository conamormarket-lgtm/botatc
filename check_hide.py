import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()
    print("SUCCESS regex hide:", "<a href=\"/settings\"" in text)

import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target1 = r"""word-wrap:break-word; max-width:75%; min-width:0; padding:12px 16px; border-radius:18px; position:relative;"""
rep1 = r"""word-wrap:break-word; overflow-wrap:anywhere; max-width:85%; min-width:0; padding:8px 12px; border-radius:18px; position:relative; box-sizing:border-box; overflow:hidden;"""

if target1 in text:
    text = text.replace(target1, rep1)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched speech bubble!")
else:
    print("Speech bubble not found")

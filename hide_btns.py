import sys
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

rep = """
    with open("inbox.html", "r", encoding="utf-8") as f:
        html = f.read()

    if not es_admin(request):
        import re
        html = re.sub(r'<a href="/settings".*?</a>', '', html, flags=re.DOTALL)
        html = re.sub(r'<a href="/admin".*?</a>', '', html, flags=re.DOTALL)
        html = re.sub(r'<a href="/usuarios".*?</a>', '', html, flags=re.DOTALL)
        html = re.sub(r'<!-- Admin Users Icon -->.*?</a>', '', html, flags=re.DOTALL)
"""

import re
text = re.sub(r'with open\("inbox\.html", "r", encoding="utf-8"\) as f:\s*html = f\.read\(\)', rep, text)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Injected admin hiding logic in inbox renderer")

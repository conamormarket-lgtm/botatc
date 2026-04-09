import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix the broken line
text = re.sub(r'remitente = "🤖 María" if es_bot else f"👤 \{nombre\}"\s*texto     = m\["content"\]\.replace\("\\n", "<br>"\)',
              r'remitente = "🤖 María" if es_bot else f"👤 {nombre}"\n        texto     = m["content"].replace("\\n", "<br>")', text)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Syntax fixed")

import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'elif tipo_mensaje == "document":.*?filename \}\]"', text, flags=re.DOTALL)
if m:
    replacement = r"""elif tipo_mensaje == "document":
            filename = mensaje_data.get("document", {}).get("filename", "documento")
            media_id = mensaje_data.get("document", {}).get("id", "")
            texto_cliente = f"[documento:{media_id}|{filename}]" """
    text = text.replace(m.group(0), replacement)
    print("Replaced document handler")
else:
    print("Not found")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
    print("Done")

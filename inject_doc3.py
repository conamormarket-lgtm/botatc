import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'elif tipo_mensaje == "document":.*?\]"', text, flags=re.DOTALL)
if m:
    replacement = r"""elif tipo_mensaje == "document":
            filename = mensaje_data.get("document", {}).get("filename", "archivo")
            media_id = mensaje_data.get("document", {}).get("id", "")
            texto_cliente = f"[documento:{media_id}|{filename}]" """
    text = text.replace(m.group(0), replacement)
    print("Replaced document ingestion")
else:
    print("Ingestion block not found")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)


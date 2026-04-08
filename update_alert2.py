import re
with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

old = 'alert("Error subiendo el audio a los servidores de WhatsApp");'
new = 'alert("Error procesando o subiendo el audio:\\n\\n" + (data.error || "Rechazo desconocido en el servidor."));'
text = text.replace(old, new)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated inbox.html alert")

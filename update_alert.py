import re
with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

old_alert = 'alert("El servidor de WhatsApp (Meta) rechazó o no pudo procesar el formato del audio.");'
new_alert = 'alert("El servidor de WhatsApp (Meta) rechazó o no pudo procesar el formato del audio.\\n\\nDetalle técnico: " + (enviaRes?.error || "Desconocido"));'

if 'Detalle técnico' not in text:
    text = text.replace(old_alert, new_alert)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated alert in inbox.html")

import sys
import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

rep = """        if not s:
            # Create a brand new session if it doesn't exist so it appears in Inbox immediately
            s = {
                "historial": [], 
                "estado_bot": "activo",
                "etiquetas": [],
                "ultimo_mensaje": "",
                "clienteNombre": "Desconocido (Plantilla saliente)"
            }
        
        if "historial" not in s: s["historial"] = []
"""

text = re.sub(r'        if s:\n            if "historial" not in s: s\["historial"\] = \[\]', rep, text)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated server.py api_enviar_plantilla to create new sessions")

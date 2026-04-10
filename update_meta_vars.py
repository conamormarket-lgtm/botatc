import sys
import re

with open("whatsapp_client.py", "r", encoding="utf-8") as f:
    text = f.read()

rep = """
    if components is not None:
        if len(components) > 0 and isinstance(components[0], str):
            # Se pasaron parametros simples (texto)
            structured_params = [{"type": "text", "text": str(c)} for c in components]
            template_data["components"] = [{
                "type": "body",
                "parameters": structured_params
            }]
        else:
            # Se paso la estructura compleja
            template_data["components"] = components
"""

text = re.sub(r'if components:\s*template_data\["components"\] = components', rep, text)

with open("whatsapp_client.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Actualizada funcion para empaquetar variables en formato META")

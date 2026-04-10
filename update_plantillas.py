import sys
import re

with open("whatsapp_client.py", "r", encoding="utf-8") as f:
    text = f.read()

rep = """async def enviar_plantilla(numero_destino: str, template_name: str, language_code: str = "es", components: list = None) -> str | None:
    \"\"\"Envía un Message Template preaprobado por Meta, soportando variables dinámicas.\"\"\"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    
    template_data = {
        "name": template_name,
        "language": {"code": language_code}
    }
    
    if components:
        template_data["components"] = components
        
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "template",
        "template": template_data
    }
"""

text = re.sub(r'async def enviar_plantilla.*?\}\n    \}', rep, text, flags=re.DOTALL)

with open("whatsapp_client.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Actualizada la función de plantillas web")

import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("prompts.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
rep = 'REGLAS CRÍTICAS — SÍGUELAS SIN EXCEPCIÓN:\\n0. SIEMPRE debes referirte al cliente usando ÚNICAMENTE el "Nombre del cliente" que se te proporciona en tus DATOS DEL PEDIDO adjuntos. Ignora cualquier otro nombre genérico o apodo de WhatsApp.'
text = re.sub(r'REGLAS CRÍTICAS — SÍGUELAS SIN EXCEPCIÓN:', rep, text)

with open("prompts.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Replaced prompt rules for names using Regex")

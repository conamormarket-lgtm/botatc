import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("prompts.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
rep = 'REGLAS CRÍTICAS — SÍGUELAS SIN EXCEPCIÓN:\\n0. SIEMPRE debes referirte y saludar al cliente usando ÚNICAMENTE el nombre que figura explícitamente como "Nombre del cliente" en la sección DATOS DE LOS PEDIDOS DEL CLIENTE que te adjunto debajo. Ignora cualquier otro nombre o apodo que figure en la plataforma de WhatsApp. Si no hay datos, refiérete a él simplemente como "Estimado cliente".'
text = re.sub(r'REGLAS CRÍTICAS — SÍGUELAS SIN EXCEPCIÓN:(.*?)\n\n1\.', rep + r'\nn1.', text, flags=re.DOTALL) # In case my previous replace was there

if '0. SIEMPRE' not in text:
    text = re.sub(r'REGLAS CRÍTICAS — SÍGUELAS SIN EXCEPCIÓN:\n', rep + r'\n1. ', text)

with open("prompts.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Prompt robustecido")

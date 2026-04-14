import os
import re

env_file = ".env"

if not os.path.exists(env_file):
    print(f"Error: No se encontró el archivo {env_file} en este directorio.")
    exit(1)

with open(env_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Buscar FIREBASE_JSON multilineal
match = re.search(r'FIREBASE_JSON=({[^}]+})', text, re.DOTALL)
if match:
    json_block = match.group(1)
    
    # Si ya está en una sola línea, no hacemos nada drástico
    if '\n' not in json_block:
        print("El archivo .env parece correcto o el JSON ya está en una sola línea.")
    else:
        # Colapsarlo a una sola línea y envolver en comillas simples
        single_line_json = ''.join([line.strip() for line in json_block.splitlines()])
        new_text = text.replace(match.group(0), "FIREBASE_JSON='" + single_line_json + "'")
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print("¡Éxito! El archivo .env ha sido reparado correctamente.")
        print("Por favor, reinicia tu servidor con: sudo systemctl restart bot-crm.service")
else:
    print("No se encontró una bloque FIREBASE_JSON roto que reparar.")

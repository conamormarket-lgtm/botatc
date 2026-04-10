import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = '''        # Renderizar Chat Activo
        s = sesiones[wa_id]
        nombre_chat = s.get("nombre_cliente", wa_id)'''

rep = '''        # Renderizar Chat Activo
        s = s_fake_vg if s_fake_vg else sesiones[wa_id]
        nombre_chat = s.get("nombre_cliente", wa_id)'''

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced s mapping")
else:
    print("Target not found")

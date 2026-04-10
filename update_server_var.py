import sys

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = 'sesion["historial"][0] = {"role": "system", "content": get_system_prompt(sesion["datos_pedido"])}'
rep = 'sesion["historial"][0] = {"role": "system", "content": get_system_prompt(pedidos_no_diseno)}'

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced prompt variable")
else:
    print("Target not found")

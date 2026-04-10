import sys
import re

with open("prompts.py", "r", encoding="utf-8") as f:
    text = f.read()

target = 'IMPORTANTE: Si el cliente consulta sobre su pedido y tiene más de uno, pregúntale amable y explícitamente sobre cuál de los pedidos mencionados necesita ayuda, dándole los detalles por ID o producto.\\n'
rep = 'IMPORTANTE: Si el cliente consulta sobre su pedido y el sistema te muestra información de MÁS DE UN PEDIDO, DEBES basar tu atención y responder asumiendo el pedido MÁS RECIENTE (Pedido 1). Sin embargo, si el cliente te aclara que no se refiere a ese pedido o menciona estar buscando otros, infórmale qué otros pedidos activos tiene en sistema (menciónalos) y pregúntale sobre cuál de ellos desea saber.\\n'

if target in text:
    text = text.replace(target, rep)
    with open("prompts.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced prompt rules")
else:
    print("Target not found")

import re

respuesta_final = 'Entendido. Agradezco la aclaración. \nTu pedido N° 007495 sigue "En Impresión" y estamos trabajando en [sticker:quedo atento.webp]'

partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\])', respuesta_final)
print("Partes:", partes)
for p in partes:
    p = p.strip()
    if not p: continue
    print("Manda:", repr(p))

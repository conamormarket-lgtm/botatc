with open('server.py', 'r', encoding='utf-8') as f:
    raw = f.read()

# Ver los bytes exactos del boton X
idx = raw.find('rightSidebar')
hits = []
start = 0
while True:
    idx = raw.find('rightSidebar', start)
    if idx == -1:
        break
    hits.append(idx)
    start = idx + 1

# El boton X debe ser el de pos 232965 aprox
for h in hits:
    snippet = raw[h:h+50]
    if 'none' in snippet and 'display' in snippet:
        # Mostrar bytes exactos
        exact = raw[h-20:h+70]
        print(f'pos {h}:')
        print(f'  str: {exact}')
        print(f'  bytes: {exact.encode("utf-8")}')
        print()

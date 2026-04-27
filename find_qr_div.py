with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

# El primer qrSearchFilter (en el rightSidebar)
# Buscar todos los qrSearchFilter y tomar el que está en el rightSidebar HTML
import re
hits = [m.start() for m in re.finditer(r'qrSearchFilter', c)]
print(f'Total hits: {len(hits)}')
for h in hits:
    ctx = c[h-300:h+50]
    if 'input type' in ctx or 'placeholder' in ctx:
        print(f'\npos {h}:')
        print(repr(c[h-400:h+100]))
        break

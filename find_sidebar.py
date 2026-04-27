with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

import re

# Encontrar la funcion cargarQuickReplies
idx = c.find('async function cargarQuickReplies')
if idx == -1:
    idx = c.find('function cargarQuickReplies')
print(f'cargarQuickReplies en pos: {idx}')
print(repr(c[idx:idx+1500]))

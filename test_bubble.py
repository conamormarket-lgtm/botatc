import re
msgs = [{'role': 'user', 'content': '[sticker:1467394604826354]'},
        {'role': 'assistant', 'content': '¡Entiendo!'}
]

burbujas = ''
for m in msgs:
    es_bot = m['role'] == 'assistant'
    clase  = 'bubble-bot' if es_bot else 'bubble-user'
    lado   = 'lado-izq' if es_bot else 'lado-der'
    texto  = m['content'].replace('\n', '<br>')
            
    match_sticker = re.match(r'^\[sticker:([^\]]+)\]$', texto.strip())
    match_imagen = re.match(r'^\[imagen:([^\]]+)\]\s*(.*)$', texto.strip())
            
    if match_sticker: texto = f'<img src="/api/media/{match_sticker.group(1)}">'
    elif match_imagen: texto = f'<img src="/api/media/{match_imagen.group(1)}">'
    print(f'TEXTO_GENERADO para {m["role"]}: {texto}')
    burbujas += f'<div class="bubble {clase} {lado}">{texto}</div>'

print('---')
print(burbujas)

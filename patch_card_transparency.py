content = open('server.py', 'r', encoding='utf-8').read()

old = "        css += f'''\n        .appearance-card, .proactive-card, .pdf-card, .backup-card, .editor-card {{\n            background: var(--accent-bg) !important;\n            border: 1px solid var(--accent-border) !important;\n        }}\n        '''\n"

new = "    # Transparencia global de todas las tarjetas del sistema (siempre, con o sin wallpaper)\n    css += '''\n    .appearance-card, .proactive-card, .pdf-card, .backup-card, .editor-card,\n    .stat-card, .table-card, .qr-card {\n        background: var(--accent-bg) !important;\n        border: 1px solid var(--accent-border) !important;\n    }\n    '''\n"

if old in content:
    content = content.replace(old, new, 1)
    open('server.py', 'w', encoding='utf-8').write(content)
    print('OK: bloque reemplazado correctamente')
else:
    idx = content.find('.appearance-card, .proactive-card')
    print('NO MATCH. Contexto:')
    print(repr(content[idx-100:idx+350]))

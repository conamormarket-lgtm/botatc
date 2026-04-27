# Quitar .stat-card, .table-card, .qr-card del bloque !important
# Esas tarjetas ya tienen inline style hardcodeado en el HTML
# El !important del CSS class estaba pisando el inline style

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """    css += '''
    .appearance-card, .proactive-card, .pdf-card, .backup-card, .editor-card,
    .stat-card, .table-card, .qr-card {
        background: var(--accent-bg) !important;
        border: 1px solid var(--accent-border) !important;
    }
    '''"""

new = """    css += '''
    .appearance-card, .proactive-card, .pdf-card, .backup-card, .editor-card {
        background: var(--accent-bg) !important;
        border: 1px solid var(--accent-border) !important;
    }
    '''"""

if old in content:
    content = content.replace(old, new, 1)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: .stat-card y .table-card removidos del bloque !important')
else:
    print('NO MATCH - buscando...')
    idx = content.find('Transparencia global')
    print(repr(content[idx:idx+350]))

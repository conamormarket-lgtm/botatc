import re

CARD_STYLE = 'background:var(--accent-bg);border:1px solid var(--accent-border);border-radius:12px;'

def patch_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    count = 0
    
    # Patron 1: <div class="stat-card"> sin style
    def add_style_no_existing(m):
        nonlocal count
        count += 1
        return f'<div class="stat-card" style="{CARD_STYLE}">'
    
    # Patron 2: <div class="stat-card" style="..."> con style existente
    def add_style_existing(m):
        nonlocal count
        existing = m.group(1)
        # No duplicar si ya tiene background
        if 'background' in existing:
            return m.group(0)
        count += 1
        return f'<div class="stat-card" style="{CARD_STYLE}{existing}">'
    
    # stat-card sin style
    content = re.sub(
        r'<div class="stat-card">',
        add_style_no_existing,
        content
    )
    
    # stat-card con style existente
    content = re.sub(
        r'<div class="stat-card" style="([^"]*)">', 
        add_style_existing, 
        content
    )
    
    # table-card sin style  
    def add_table_no_style(m):
        nonlocal count
        count += 1
        return f'<div class="table-card" style="{CARD_STYLE}padding:2rem;">'
    
    # table-card con style existente (preservar padding y otras props)
    def add_table_existing(m):
        nonlocal count
        existing = m.group(1)
        if 'background' in existing:
            return m.group(0)
        count += 1
        return f'<div class="table-card" style="{CARD_STYLE}{existing}">'
    
    content = re.sub(
        r'<div class="table-card">',
        add_table_no_style,
        content
    )
    
    content = re.sub(
        r'<div class="table-card" style="([^"]*)">', 
        add_table_existing, 
        content
    )
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'{filename}: {count} elementos actualizados')
    
    # Verificar
    if 'background:var(--accent-bg)' in content:
        print(f'  OK - inline style inyectado correctamente')
    
    return count

patch_file('admin.html')
patch_file('usuarios.html')

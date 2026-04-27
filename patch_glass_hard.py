# Reemplaza el background de stat-card y table-card con glassmorphism hardcodeado
# igual al appearance-card pero sin CSS variables que puedan fallar

GLASS_BG = 'background:rgba(255,255,255,0.04);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.08);border-radius:12px;'

import re

for filename in ['admin.html', 'usuarios.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Reemplazar TODOS los stat-card y table-card que ya tienen inline style con background
    # (los que se agregaron en el patch anterior)
    def replace_card_style(m):
        classes = m.group(1)  # stat-card o table-card
        existing_style = m.group(2)
        
        # Quitar cualquier background existente
        existing_style = re.sub(r'background:[^;]+;?', '', existing_style)
        existing_style = re.sub(r'border:[^;]+;?', '', existing_style)
        existing_style = re.sub(r'border-radius:[^;]+;?', '', existing_style)
        # Limpiar espacios dobles
        existing_style = existing_style.strip().strip(';')
        
        if existing_style:
            return f'<div class="{classes}" style="{GLASS_BG}{existing_style};">'
        else:
            return f'<div class="{classes}" style="{GLASS_BG}">'
    
    # Con style existente
    content = re.sub(
        r'<div class="(stat-card|table-card)" style="([^"]*)">', 
        replace_card_style,
        content
    )
    
    # Sin style (por si quedaron sin estilo)
    content = re.sub(
        r'<div class="(stat-card|table-card)">',
        lambda m: f'<div class="{m.group(1)}" style="{GLASS_BG}">',
        content
    )
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'{filename}: OK')

# Verificar resultado
with open('admin.html', 'r', encoding='utf-8') as f:
    c = f.read()
# Contar cuántos tienen el nuevo estilo
count = c.count('rgba(255,255,255,0.04)')
print(f'admin.html: {count} elementos con glassmorphism hardcodeado')

with open('usuarios.html', 'r', encoding='utf-8') as f:
    c = f.read()
count = c.count('rgba(255,255,255,0.04)')
print(f'usuarios.html: {count} elementos con glassmorphism hardcodeado')

# Confirmar que todos los stat-card y table-card de admin.html tienen el glassmorphism correcto

with open('admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar cualquier residuo antiguo con el glassmorphism correcto
import re

GLASS = 'background:rgba(255,255,255,0.04);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.08);border-radius:12px;'

def fix_card(m):
    cls = m.group(1)
    existing = m.group(2) if m.group(2) else ''
    # quitar background, border y border-radius del style existente
    existing = re.sub(r'background:[^;]+;?', '', existing)
    existing = re.sub(r'border(?!-left|-radius):[^;]+;?', '', existing)
    existing = re.sub(r'border-radius:[^;]+;?', '', existing)
    existing = re.sub(r'backdrop-filter:[^;]+;?', '', existing)
    existing = re.sub(r'-webkit-backdrop-filter:[^;]+;?', '', existing)
    existing = existing.strip().strip(';').strip()
    if existing:
        return f'<div class="{cls}" style="{GLASS}{existing};">'
    return f'<div class="{cls}" style="{GLASS}">'

# Con style
content = re.sub(r'<div class="(stat-card|table-card)" style="([^"]*)">', fix_card, content)
# Sin style
content = re.sub(r'<div class="(stat-card|table-card)">', lambda m: f'<div class="{m.group(1)}" style="{GLASS}">', content)

with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

count = content.count('rgba(255,255,255,0.04)')
print(f'admin.html: {count} elementos con glassmorphism transparente')

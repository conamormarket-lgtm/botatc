import re

with open('admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

GLASS_STYLE = 'background:var(--accent-bg);border:1px solid var(--accent-border);border-radius:12px;'

# stat-card sin style existente
content = re.sub(
    r'<div class="stat-card">',
    f'<div class="stat-card" style="{GLASS_STYLE}">',
    content
)

# stat-card con style existente (solo border-left especiales - NO agregar background de nuevo)
def fix_stat_existing(m):
    existing = m.group(1)
    if 'background' in existing:
        return m.group(0)  # ya tiene, no tocar
    return f'<div class="stat-card" style="{GLASS_STYLE}{existing}">'

content = re.sub(
    r'<div class="stat-card" style="([^"]*)">', 
    fix_stat_existing,
    content
)

# table-card sin style existente
content = re.sub(
    r'<div class="table-card">',
    f'<div class="table-card" style="{GLASS_STYLE}padding:1.5rem;">',
    content
)

# table-card con style existente (padding, display:flex, etc.)
def fix_table_existing(m):
    existing = m.group(1)
    if 'background' in existing:
        return m.group(0)
    return f'<div class="table-card" style="{GLASS_STYLE}{existing}">'

content = re.sub(
    r'<div class="table-card" style="([^"]*)">', 
    fix_table_existing,
    content
)

with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verificar
stat = re.findall(r'<div class="stat-card[^>]*>', content)
tables = re.findall(r'<div class="table-card[^>]*>', content)
print('stat-cards:')
for s in stat:
    print(' ', s[:100])
print('table-cards:')
for t in tables:
    print(' ', t[:100])

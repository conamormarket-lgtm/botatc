import re

with open('admin.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Revertir stat-cards al estado original (sin inline background)
c = re.sub(
    r'<div class="stat-card" style="background:rgba\(255,255,255,0\.04\)[^"]*border-left: 3px solid var\(--primary-hover\);">',
    '<div class="stat-card" style="border-left: 3px solid var(--primary-hover);">',
    c
)
c = re.sub(
    r'<div class="stat-card" style="background:rgba\(255,255,255,0\.04\)[^"]*border-left: 3px solid var\(--danger-color\);">',
    '<div class="stat-card" style="border-left: 3px solid var(--danger-color);">',
    c
)
c = re.sub(
    r'<div class="stat-card" style="background:rgba\(255,255,255,0\.04\)[^"]*">',
    '<div class="stat-card">',
    c
)

# Revertir table-cards al estado original
c = re.sub(
    r'<div class="table-card" style="background:rgba\(255,255,255,0\.04\)[^"]*padding: 2\.5rem;">',
    '<div class="table-card" style="padding: 2.5rem;">',
    c
)
c = re.sub(
    r'<div class="table-card" style="background:rgba\(255,255,255,0\.04\)[^"]*display:flex[^"]*">',
    '<div class="table-card" style="padding: 2.5rem; display:flex; flex-direction:column; align-items:center; gap: 1rem; text-align:center;">',
    c
)
# Cualquier otro table-card con background rgba
c = re.sub(
    r'<div class="table-card" style="background:rgba\(255,255,255,0\.04\)[^"]*">',
    '<div class="table-card">',
    c
)

# Restaurar el background original en el CSS de .stat-card si fue cambiado
# (ya deberia estar sin background por cambios anteriores - asi lo dejamos)

with open('admin.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('OK - admin.html revertido')

# Verificar
import re
stat_cards = re.findall(r'<div class="stat-card[^>]*>', c)
table_cards = re.findall(r'<div class="table-card[^>]*>', c)
print('stat-cards:', stat_cards)
print('table-cards:', [x[:80] for x in table_cards])

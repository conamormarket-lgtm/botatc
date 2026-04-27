import re

content = open('admin.html', 'r', encoding='utf-8').read()

print("=== CSS RULES para .stat-card y .table-card ===")
for match in re.finditer(r'(\.stat-card|\.table-card)[^{]*\{[^}]+\}', content, re.DOTALL):
    print('FOUND:', repr(match.group()))
    print('---')

print()
print("=== INLINE STYLES en elementos con esas clases ===")
for match in re.finditer(r'class="[^"]*(?:stat-card|table-card)[^"]*"[^>]*>', content):
    print('TAG:', repr(match.group()[:300]))
    print('---')

print()
print("=== Verificando si custom_theme_css placeholder existe ===")
if '{custom_theme_css}' in content:
    print("SI tiene placeholder {custom_theme_css}")
else:
    print("NO tiene placeholder - se inyecta antes de </head>")

# Verificar settings.html tambien
content2 = open('settings.html', 'r', encoding='utf-8').read()
print()
print("=== settings.html - ¿tiene {custom_theme_css}? ===")
if '{custom_theme_css}' in content2:
    print("SI tiene placeholder")
else:
    print("NO tiene placeholder")

# Buscar appearance-card CSS en settings
print()
print("=== settings.html - appearance-card CSS ===")
for match in re.finditer(r'\.appearance-card[^{]*\{[^}]+\}', content2, re.DOTALL):
    print('FOUND:', repr(match.group()))
    print('---')

with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

# El valor original era 0.65 - alguien lo cambio a 0.25
old = '_panel_glass = f"rgba({_r}, {_g}, {_b}, 0.25)"'
new = '_panel_glass = f"rgba({_r}, {_g}, {_b}, 0.65)"'

if old in c:
    c = c.replace(old, new, 1)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('OK - panel-glass restaurado de 0.25 a 0.65')
else:
    print('NO MATCH, buscando variantes...')
    idx = c.find('_panel_glass = f')
    if idx >= 0:
        print(repr(c[idx:idx+60]))

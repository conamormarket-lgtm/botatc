with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

old = 'padding:1rem 1.5rem; border-bottom:1px solid var(--accent-border); background:transparent;'
new = 'padding:1rem 1.5rem; background:transparent;'

if old in c:
    c = c.replace(old, new, 1)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('OK - border-bottom eliminado')
else:
    print('NO MATCH')

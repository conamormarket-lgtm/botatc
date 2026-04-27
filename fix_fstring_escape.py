with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

# El onclick malo tiene llaves JS sin escapar dentro del f-string de Python
old = (
    """<h4 onclick="var tl=document.getElementById('templateList');"""
    """var ar=document.getElementById('plantArrow');"""
    """if(tl.style.display==='none'){tl.style.display='block';ar.textContent='▾'}"""
    """else{tl.style.display='none';ar.textContent='▸'}" """
)
new = (
    """<h4 onclick="var tl=document.getElementById('templateList');"""
    """var ar=document.getElementById('plantArrow');"""
    """if(tl.style.display==='none'){{tl.style.display='block';ar.textContent='\\u25be'}}"""
    """else{{tl.style.display='none';ar.textContent='\\u25b8'}}" """
)

if old in c:
    c = c.replace(old, new, 1)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('OK - llaves JS escapadas correctamente')
else:
    # Buscar y mostrar la linea exacta para diagnostico
    import re
    m = re.search(r'plantArrow.*?▸', c)
    if m:
        print('Encontrado en pos', m.start())
        print(repr(c[m.start()-20:m.end()+50]))
    else:
        print('NO ENCONTRADO')

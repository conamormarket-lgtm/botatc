with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

# ── CAMBIO 1: El sidebar NO se cierra al usar una QR ──────────────────────
MARKER = "document.getElementById('rightSidebar').style.display = 'none';"
if MARKER in c:
    # Solo eliminar la linea (y el newline siguiente) dentro del contexto de usarQR
    # Hacerlo con una sola sustitucion segura
    c = c.replace(
        "document.getElementById('rightSidebar').style.display = 'none';\n                \n                const form",
        "// sidebar permanece abierto tras usar QR\n                const form",
        1
    )
    print('OK 1: sidebar no se cierra al usar QR')
else:
    print('NO MATCH 1')

# ── CAMBIO 2: Plantillas (Meta) header desplegable ────────────────────────
import re

# Buscar el div contenedor del header de Plantillas
m = re.search(r'<h4 style="[^"]*">Plantillas \(Meta\)</h4>', c)
if m:
    old2 = m.group(0)
    new2 = (
        '<h4 onclick="'
        "var tl=document.getElementById('templateList');"
        "var ar=document.getElementById('plantArrow');"
        "if(tl.style.display==='none'){tl.style.display='block';ar.textContent='▾'}"
        "else{tl.style.display='none';ar.textContent='▸'}"
        '" style="margin:0; font-size:0.85rem; color:var(--text-main); font-weight:600; cursor:pointer; display:flex; align-items:center; gap:0.4rem; user-select:none;">'
        '<span id="plantArrow" style="font-size:0.75rem;">▾</span>Plantillas (Meta)</h4>'
    )
    c = c.replace(old2, new2, 1)
    print('OK 2: Plantillas header desplegable')
else:
    print('NO MATCH 2')

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done')

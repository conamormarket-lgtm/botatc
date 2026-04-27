import sys, os
sys.path.insert(0, os.getcwd())

# Importar la función real
try:
    from server import inyectar_tema_global, active_sessions
    print("OK: importado server.py")
except Exception as e:
    print("ERROR importando server:", e)
    exit()

# Crear un request falso que simule al admin
class FakeRequest:
    cookies = {}

# Intentar con un token de sesion real si existe
print("Sesiones activas:", list(active_sessions.keys())[:3])

# Usar sesion vacia para probar con defaults
req = FakeRequest()

with open('admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('{main_nav_html}', '<nav>NAV</nav>')
html = html.replace('{color_global}', '#10b981')
html = html.replace('{class_btn_toggle}', '')
html = html.replace('{txt_btn_toggle}', 'Toggle IA')

result = inyectar_tema_global(req, html)

# Buscar el bloque CSS inyectado
import re
styles = re.findall(r'<style[^>]*>(.*?)</style>', result, re.DOTALL)
for i, s in enumerate(styles):
    if 'accent-bg' in s or 'stat-card' in s or 'appearance-card' in s:
        print(f'\n=== STYLE BLOCK {i} con accent-bg/stat-card ===')
        print(s[:2000])

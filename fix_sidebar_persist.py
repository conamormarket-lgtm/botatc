with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

# El boton X usa comillas simples REGULARES (no backslash-escaped)
# onclick="document.getElementById('rightSidebar').style.display='none'"
old_x = "document.getElementById('rightSidebar').style.display='none'"
new_x = "document.getElementById('rightSidebar').style.display='none';localStorage.setItem('qrSidebarOpen','0')"

count = c.count(old_x)
print(f'Ocurrencias: {count}')
if count > 0:
    c = c.replace(old_x, new_x, 1)
    print('OK: boton X guarda estado en localStorage')
else:
    print('SIGUE SIN MATCH')

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(c)

import subprocess
result = subprocess.run(['python', '-m', 'py_compile', 'server.py'], capture_output=True, text=True)
print('Compilacion:', 'OK' if result.returncode == 0 else result.stderr[:200])

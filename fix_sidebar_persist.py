with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Buscar el restore script que insertamos antes
old_restore = (
    "\n        // Restaurar estado del sidebar desde localStorage\n"
    "        (function(){{\n"
    "          if(localStorage.getItem('qrSidebarOpen')==='1'){{\n"
    "            var s=document.getElementById('rightSidebar');\n"
    "            if(s){{s.style.display='flex';"
    "if(window.cargarQuickReplies)window.cargarQuickReplies();"
    "if(window.cargarPlantillas)window.cargarPlantillas();}}\n"
    "          }}\n"
    "        }})();\n"
)

# Nuevo: esperar al evento load para que las funciones esten definidas
new_restore = (
    "\n        // Restaurar estado del sidebar desde localStorage\n"
    "        window.addEventListener('load', function(){{\n"
    "          if(localStorage.getItem('qrSidebarOpen')==='1'){{\n"
    "            var s=document.getElementById('rightSidebar');\n"
    "            if(s){{\n"
    "              s.style.display='flex';\n"
    "              setTimeout(function(){{\n"
    "                if(window.cargarQuickReplies) window.cargarQuickReplies();\n"
    "                if(window.cargarPlantillas) window.cargarPlantillas();\n"
    "              }}, 100);\n"
    "            }}\n"
    "          }}\n"
    "        }});\n"
)

if old_restore in c:
    c = c.replace(old_restore, new_restore, 1)
    print('OK: restore script actualizado para usar window.load')
else:
    print('NO MATCH - buscando fragmento...')
    idx = c.find('Restaurar estado del sidebar')
    if idx >= 0:
        print(f'Encontrado en pos {idx}:')
        print(repr(c[idx:idx+400]))

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(c)

import subprocess
result = subprocess.run(['python', '-m', 'py_compile', 'server.py'], capture_output=True, text=True)
print('Compilacion:', 'OK' if result.returncode == 0 else result.stderr[:300])

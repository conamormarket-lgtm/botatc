import sys
import re

with open("server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

admin_routes = ["/settings", "/api/settings", "/usuarios", "/api/usuarios"]

flag_admin = False
for i, line in enumerate(lines):
    if line.startswith("@app."):
        flag_admin = any(r in line for r in admin_routes)
        
    if flag_admin and "if not verificar_sesion(request):" in line:
        lines[i] = line.replace("verificar_sesion", "es_admin")

with open("server.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
    
print("Updated /settings and /usuarios to use es_admin")

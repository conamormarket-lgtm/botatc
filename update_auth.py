import sys
import os

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Update verificar_sesion to load from Firebase properly when needed, or just return bool.
# We'll update the active_sessions dict to store the full user dictionary!

rep = """
def obtener_usuario_sesion(request: Request) -> dict | None:
    token = request.cookies.get("session_token")
    if token and token in active_sessions:
        return active_sessions[token]
    return None

def verificar_sesion(request: Request):
    user = obtener_usuario_sesion(request)
    if user and user.get("estado") == "aprobado":
        return True
    return False

def es_admin(request: Request):
    user = obtener_usuario_sesion(request)
    return user and "admin" in user.get("permisos", []) and user.get("estado") == "aprobado"

@app.get("/login", response_class=HTMLResponse)
"""

import re
text = re.sub(r'def verificar_sesion[^@]+@app\.get\("/login", response_class=HTMLResponse\)', rep, text)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Replaced auth functions")

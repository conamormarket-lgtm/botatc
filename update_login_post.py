import sys
import os

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

import re

rep = """
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/login")
async def login_post(response: Response, username: str = Form(...), password: str = Form(...), action: str = Form("login")):
    if action == "register":
        from firebase_client import crear_usuario
        exito = crear_usuario(username, hash_password(password))
        if exito:
            return HTMLResponse(obtener_login_html(error="Cuenta creada. Espera a que un administrador la apruebe.", success=True), status_code=200)
        else:
            return HTMLResponse(obtener_login_html(error="El usuario ya existe."), status_code=400)

    # Es Login
    from firebase_client import obtener_usuario
    # Soporte para la cuenta admin inicial de rescate
    if username == "admin" and password == ADMIN_PASSWORD:
        user_data = {"username": "admin", "estado": "aprobado", "permisos": ["admin"]}
    else:
        user_data = obtener_usuario(username)
        if not user_data or user_data.get("password") != hash_password(password):
            return HTMLResponse(obtener_login_html(error="Usuario o clave incorrectos."), status_code=401)
        
        if user_data.get("estado") != "aprobado":
            return HTMLResponse(obtener_login_html(error="Tu cuenta está pendiente de aprobación por un administrador."), status_code=403)

    import uuid
    token = str(uuid.uuid4())
    active_sessions[token] = user_data
    save_sessions()
    
    # Redirigir al inbox por defecto
    resp = RedirectResponse(url="/inbox", status_code=303)
    resp.set_cookie(key="session_token", value=token, httponly=True, max_age=86400)
    return resp

@app.get("/logout")
"""

text = re.sub(r'@app\.post\("/login"\)[^@]+@app\.get\("/logout"\)', rep, text)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated POST logic")

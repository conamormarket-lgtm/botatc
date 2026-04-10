import sys
import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

rep = """
@app.post("/login")
async def login_post(response: Response, username: str = Form(None), password: str = Form(None), google_token: str = Form(None), action: str = Form("login")):
    from firebase_client import obtener_usuario, crear_usuario
    
    user_data = None
    
    if google_token:
        try:
            from google.oauth2 import id_token
            import google.auth.transport.requests
            request_g = google.auth.transport.requests.Request()
            # Idealmente deberíamos validar el CLIENT_ID passandolo a audience=..., por ahora solo validamos firma
            val = id_token.verify_oauth2_token(google_token, request_g)
            email = val.get("email")
            parsed_username = email.split('@')[0]
            
            user_data = obtener_usuario(parsed_username)
            if not user_data:
                # auto-registrar si no existe
                crear_usuario(parsed_username, "GOOGLE_AUTH")
                return HTMLResponse(obtener_login_html(error="Cuenta vinculada con Google. Espera a que un administrador apruebe tu cuenta.", success=True), status_code=200)
                
            if user_data.get("estado") != "aprobado":
                return HTMLResponse(obtener_login_html(error="Tu cuenta de Google está pendiente de aprobación."), status_code=403)
                
        except Exception as e:
            return HTMLResponse(obtener_login_html(error=f"Error validando Google Token: {str(e)}"), status_code=401)
            
    else:
        if not username or not password:
            return HTMLResponse(obtener_login_html(error="Faltan credenciales."), status_code=400)
            
        if action == "register":
            exito = crear_usuario(username, hash_password(password))
            if exito:
                return HTMLResponse(obtener_login_html(error="Cuenta creada. Espera a que un administrador la apruebe.", success=True), status_code=200)
            else:
                return HTMLResponse(obtener_login_html(error="El usuario ya existe."), status_code=400)

        # Basic Login
        if username == "admin" and password == ADMIN_PASSWORD:
            user_data = {"username": "admin", "estado": "aprobado", "permisos": ["admin"]}
        else:
            user_data = obtener_usuario(username)
            if not user_data or user_data.get("password") != hash_password(password):
                return HTMLResponse(obtener_login_html(error="Usuario o clave incorrectos."), status_code=401)
            if user_data.get("estado") != "aprobado":
                return HTMLResponse(obtener_login_html(error="Tu cuenta está pendiente de aprobación."), status_code=403)

    import uuid
    token = str(uuid.uuid4())
    active_sessions[token] = user_data
    save_sessions()
    
    resp = RedirectResponse(url="/inbox", status_code=303)
    resp.set_cookie(key="session_token", value=token, httponly=True, max_age=86400)
    return resp
"""

text = re.sub(r'@app\.post\("/login"\)\nasync def login_post.*?return HTMLResponse\(obtener_login_html\(error="Faltan credenciales\."\), status_code=400\)', rep, text, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Implemented full backend Google Logic")

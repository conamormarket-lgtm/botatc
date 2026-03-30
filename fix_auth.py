import re

with open('server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the authentication verification function with the new Cookie session system
if "def verificar_admin(" in code:
    new_auth_system = '''from fastapi import Response

VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
active_sessions = {}

def verificar_sesion(request: Request):
    token = request.cookies.get("session_token")
    return token in active_sessions

@app.get("/login", response_class=HTMLResponse)
async def login_get():
    return obtener_login_html()

@app.post("/login")
async def login_post(response: Response, username: str = Form(...), password: str = Form(...)):
    if username in VALID_USERS and VALID_USERS[username] == password:
        import uuid
        token = str(uuid.uuid4())
        active_sessions[token] = username
        resp = RedirectResponse(url="/inbox", status_code=303)
        resp.set_cookie(key="session_token", value=token, httponly=True, max_age=86400)
        return resp
    return HTMLResponse(obtener_login_html(error="Usuario o clave incorrectos."), status_code=401)

@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session_token")
    return resp

'''
    # First, strip the old `verificar_admin` function entirely
    code = re.sub(r'def verificar_admin\(password: str\):.*?hashlib\.sha256\(ADMIN_PASSWORD\.encode\(\)\)\.hexdigest\(\)', '', code, flags=re.DOTALL)
    
    # Prepend the new auth system where `obtener_login_html` starts
    code = code.replace('def obtener_login_html():', new_auth_system + 'def obtener_login_html(error=""):')

# Update obtener_login_html to accept error parameter
code = code.replace(
    'return """',
    '''err_html = f'<div class="error">{error}</div>' if error else ''
    return f"""'''
)
code = code.replace('<p class="subtitle">Ingresa la credencial maestra del sistema</p>',
    '<p class="subtitle">Ingresa tus credenciales del sistema</p>\\n      {err_html}')
code = code.replace('<form method="get">', '<form method="post" action="/login">')
code = code.replace(
    '<label>Contraseña Administrativa</label>\n        <input type="password" name="pwd" placeholder="Ingresa tu clave secreta..." autofocus>\n        <button type="submit">Desbloquear</button>',
    '<label>Usuario</label>\\n        <input type="text" name="username" placeholder="Tu usuario..." required autofocus>\\n        <label>Contraseña Administrativa</label>\\n        <input type="password" name="password" placeholder="Ingresa tu clave secreta..." required>\\n        <button type="submit">Desbloquear</button>'
)

# HTML query string artifacts
code = code.replace('?pwd={pwd}', '')
code = code.replace('&pwd={pwd}', '')
code = code.replace('?pwd={pwd}&tab={tab}', '?tab={tab}')
code = code.replace('&pwd={pwd}&tab={tab}', '&tab={tab}')
code = code.replace('?pwd=__PWD__', '')
code = code.replace(', pwd: \'__PWD__\'', '')
code = code.replace('html.replace("{pwd}", pwd)', 'html.replace("{pwd}", "")')

# Remove hidden pwd fields
code = re.sub(r'<input \s*type="hidden"\s*name="pwd"\s*value="\{pwd\}">\n\s+', '', code)
code = re.sub(r'<input\s*type="hidden"\s*name="pwd"\s*value="\{pwd\}">', '', code)

# Fix Endpoint signartures (generic stripping)
code = code.replace(', pwd: str = ""', '')
code = code.replace('pwd: str = ""', 'request: Request') # Fallback if it was the only param

code = code.replace(', pwd: str = Form(...)', '')
code = code.replace('pwd: str = Form(...)', 'request: Request')

# Specific Fixes
code = code.replace('def renderizar_inbox(pwd: str, wa_id: str = None, tab: str = "all"):', 'def renderizar_inbox(request: Request, wa_id: str = None, tab: str = "all"):')
code = code.replace('renderizar_inbox(pwd, None, tab)', 'renderizar_inbox(request, None, tab)')
code = code.replace('renderizar_inbox(pwd, wa_id, tab)', 'renderizar_inbox(request, wa_id, tab)')

code = code.replace('verificar_admin(pwd)', 'verificar_sesion(request)')

# Route cleanups
code = code.replace('url=f"/admin?pwd={pwd}"', 'url="/admin"')

# Remaining function signature fixups if Request wasn't injected correctly
code = code.replace('async def toggle_bot_global():', 'async def toggle_bot_global(request: Request):')
code = code.replace('async def reactivar_bot(numero_wa: str):', 'async def reactivar_bot(request: Request, numero_wa: str):')
code = code.replace('async def ver_chat(numero_wa: str):', 'async def ver_chat(request: Request, numero_wa: str):')

# Simulador specific fixes
code = code.replace('pwd = data.get("pwd", "")\n    if not verificar_sesion(request):', 'if not verificar_sesion(request):')

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(code)

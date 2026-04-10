import sys
import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

rep = """
@app.post("/login")
async def login_post(response: Response, username: str = Form(None), password: str = Form(None), google_token: str = Form(None), action: str = Form("login")):
    if google_token:
        # TODO: Implementar validación real de google_token (requiere instalar google-auth o usar PyJWT)
        # Por ahora, simularemos un error pidiendo configurar el client ID, o extrayendo info básica si se instalara firebase-admin auth (web)
        return HTMLResponse(obtener_login_html(error="Google Login requiere validación de token y Client ID en backend."), status_code=501)
        
    if not username or not password:
        return HTMLResponse(obtener_login_html(error="Faltan credenciales."), status_code=400)
"""

text = re.sub(r'@app\.post\("/login"\)\nasync def login_post.*?action: str = Form\("login"\)\):', rep, text, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated POST definition")

import sys
import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# First, modify args of login_post
rep1 = """@app.post("/login")
async def login_post(response: Response, username: str = Form(None), password: str = Form(None), google_token: str = Form(None), action: str = Form("login"), remember: str = Form(None)):
"""
text = re.sub(r'@app\.post\("/login"\)\nasync def login_post\(.*?\):', rep1, text)

# Second, modify cookie setting: 
# resp = RedirectResponse(url="/inbox", status_code=303)
# resp.set_cookie(key="session_token", value=token, httponly=True, max_age=86400)
# return resp

rep2 = """
    resp = RedirectResponse(url="/inbox", status_code=303)
    if remember == "yes" or google_token:
        resp.set_cookie(key="session_token", value=token, httponly=True, max_age=2592000) # 30 días
    else:
        resp.set_cookie(key="session_token", value=token, httponly=True) # cookie de sesión (se borra al cerrar el navegador)
    return resp
"""

text = re.sub(r'    resp = RedirectResponse.*?max_age=86400\)\n    return resp', rep2, text, flags=re.DOTALL)

# Third, add the checkbox to the login form
rep3 = """
            <input type="password" name="password" id="password" placeholder="Contraseña" />
            <div style="display:flex; align-items:center; margin-top:5px; font-size:13px; color:#94a3b8; user-select:none;">
                <input type="checkbox" name="remember" id="remember" value="yes" style="margin-right:8px; cursor:pointer;" checked>
                <label for="remember" style="cursor:pointer;">Mantener sesión iniciada</label>
            </div>
            <button type="submit" id="submit-btn" style="margin-top: 15px; margin-bottom: 20px;">Ingresar</button>
"""
text = re.sub(r'            <input type="password".*?/>\n            <button type="submit".*?</button>', rep3, text, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated server.py with remember me")

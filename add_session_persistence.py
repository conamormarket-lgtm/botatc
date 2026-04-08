import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Replace active_sessions initialization
old_init = '''VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
active_sessions = {}'''

new_init = '''VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
import json, os
active_sessions = {}
if os.path.exists("sessions.json"):
    try:
        with open("sessions.json", "r") as f:
            active_sessions = json.load(f)
    except:
        pass

def save_sessions():
    try:
        with open("sessions.json", "w") as f:
            json.dump(active_sessions, f)
    except:
        pass'''

if 'def save_sessions():' not in text:
    text = text.replace(old_init, new_init)

# 2. Modify login_post to save session
old_login = '''        active_sessions[token] = username
        resp = RedirectResponse(url="/inbox", status_code=303)'''

new_login = '''        active_sessions[token] = username
        save_sessions()
        resp = RedirectResponse(url="/inbox", status_code=303)'''

text = text.replace(old_login, new_login)

# 3. Modify logout to save session
old_logout = '''@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session_token")
    return resp'''

new_logout = '''@app.get("/logout")
async def logout(request: Request):
    token = request.cookies.get("session_token")
    if token in active_sessions:
        del active_sessions[token]
        save_sessions()
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session_token")
    return resp'''

text = text.replace(old_logout, new_logout)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Applied session persistence.")

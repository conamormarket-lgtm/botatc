import sys
import os

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

import re

rep = '''
def obtener_login_html(error="", success=False):
    msg_html = f'<div class="error" style="color: {"#10b981" if success else "#ef4444"}; background: {"#064e3b" if success else "#451a1e"}; border: 1px solid {"#059669" if success else "#991b1b"}; padding: 10px; border-radius: 8px; margin-bottom: 20px; font-size: 0.9em; text-align: center;">{error}</div>' if error else ''
    return f"""
    <html><head><title>Acceso Restringido — IA-ATC</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;700&display=swap" rel="stylesheet">
    <style>
      :root {{
          --primary-color: #3b82f6; --primary-hover: #2563eb;
          --bg-main: #0f172a; --bg-card: #1e293b; --text-color: #f8fafc;
      }}
      body {{
          background-color: var(--bg-main); color: var(--text-color);
          font-family: 'Inter', sans-serif; display: flex;
          align-items: center; justify-content: center; height: 100vh; margin: 0;
      }}
      .login-box {{
          background-color: var(--bg-card); padding: 40px;
          border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
          width: 100%; max-width: 350px;
      }}
      h2 {{ text-align: center; font-family: 'Outfit', sans-serif; font-size: 24px; margin-top: 0; margin-bottom: 30px; letter-spacing: -0.5px; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab-btn {{ flex: 1; padding: 10px; text-align: center; border: none; background: transparent; color: #94a3b8; font-family: 'Outfit', sans-serif; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.3s ease; }}
        .tab-btn.active {{ color: var(--primary-color); border-bottom-color: var(--primary-color); }}
      input {{
          width: 100%; padding: 12px; margin-bottom: 20px;
          border: 1px solid #334155; border-radius: 10px;
          background: #0f172a; color: white; box-sizing: border-box;
          transition: all 0.2s ease;
      }}
      input:focus {{ outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); }}
      button {{
          width: 100%; padding: 14px; background-color: var(--primary-color);
          color: white; border: none; border-radius: 10px; font-weight: 600;
          cursor: pointer; transition: background 0.3s ease, transform 0.1s ease;
      }}
      button:hover {{ background-color: var(--primary-hover); transform: translateY(-1px); }}
      button:active {{ transform: translateY(1px); }}
    </style>
    <script>
      function setMode(mode) {{
          document.getElementById('action').value = mode;
          document.getElementById('btn-login').classList.toggle('active', mode==='login');
          document.getElementById('btn-register').classList.toggle('active', mode==='register');
          document.getElementById('submit-btn').innerText = mode==='login' ? 'Ingresar' : 'Registrarse';
      }}
    </script>
    </head><body>
    <div class="login-box">
        <h2>IA-ATC</h2>
        {msg_html}
        <div class="tabs">
            <button class="tab-btn active" id="btn-login" onclick="setMode('login')">Ingresar</button>
            <button class="tab-btn" id="btn-register" onclick="setMode('register')">Registrarse</button>
        </div>
        <form method="POST" action="/login">
            <input type="hidden" id="action" name="action" value="login" />
            <input type="text" name="username" placeholder="Usuario" required autofocus autocomplete="off" />
            <input type="password" name="password" placeholder="Contraseña" required />
            <button type="submit" id="submit-btn" style="margin-top: 10px;">Ingresar</button>
        </form>
    </div>
    </body></html>
    """
'''

text = re.sub(r'def obtener_login_html\(.*?\).*?</html>\s*"""', rep, text, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated HTML")

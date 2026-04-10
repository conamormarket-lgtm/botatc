import sys
import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

rep = """
    <script src="https://accounts.google.com/gsi/client" async defer></script>
    <script>
      function setMode(mode) {
          document.getElementById('action').value = mode;
          document.getElementById('btn-login').classList.toggle('active', mode==='login');
          document.getElementById('btn-register').classList.toggle('active', mode==='register');
          document.getElementById('submit-btn').innerText = mode==='login' ? 'Ingresar' : 'Registrarse';
      }
      function handleGoogleCredential(response) {
          const form = document.createElement("form");
          form.method = "POST";
          form.action = "/login";
          const inputToken = document.createElement("input");
          inputToken.type = "hidden";
          inputToken.name = "google_token";
          inputToken.value = response.credential;
          
          const inputAction = document.createElement("input");
          inputAction.type = "hidden";
          inputAction.name = "action";
          inputAction.value = document.getElementById('action').value;
          
          form.appendChild(inputToken);
          form.appendChild(inputAction);
          document.body.appendChild(form);
          form.submit();
      }
    </script>
"""

# Insert script logic
text = re.sub(r'<script>.*?function setMode\(mode\) \{.*?</script>', rep, text, flags=re.DOTALL)

rep2 = """
        <form method="POST" action="/login" id="login-form">
            <input type="hidden" id="action" name="action" value="login" />
            <input type="text" name="username" id="username" placeholder="Usuario" autocomplete="off" />
            <input type="password" name="password" id="password" placeholder="Contraseña" />
            <button type="submit" id="submit-btn" style="margin-top: 10px; margin-bottom: 20px;">Ingresar</button>
            <div style="text-align: center; margin-bottom: 10px; font-size: 14px; color: #94a3b8;">o continúa con</div>
            <div id="g_id_onload"
                 data-client_id="REEMPLAZAR_CON_TU_CLIENT_ID"
                 data-context="use"
                 data-ux_mode="popup"
                 data-callback="handleGoogleCredential"
                 data-auto_prompt="false">
            </div>
            <div class="g_id_signin"
                 data-type="standard"
                 data-shape="rectangular"
                 data-theme="outline"
                 data-text="continue_with"
                 data-size="large"
                 data-logo_alignment="left"
                 style="display: flex; justify-content: center;">
            </div>
            <div id="google-hint" style="color: #ef4444; font-size: 11px; text-align: center; margin-top: 5px;">(Requiere configurar Client ID de Google)</div>
        </form>
"""

# Replace the form HTML
text = re.sub(r'<form method="POST" action="/login".*?</form>', rep2, text, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated HTML with Google Button")

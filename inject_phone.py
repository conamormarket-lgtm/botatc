import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add phone parser inside renderizar_inbox
target1 = r'texto  = m["content"].replace("\n", "<br>")'
replacement1 = r"""texto  = m["content"].replace("\n", "<br>")
            
            def wrap_phone(match):
                phone = match.group(1)
                clean_phone = re.sub(r'[\s\-]', '', phone)
                # Solo si tiene más de 6 dígitos
                if sum(c.isdigit() for c in clean_phone) >= 7:
                    # Escape seguro
                    return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
                return phone
            texto = re.sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)"""

if target1 in text:
    text = text.replace(target1, replacement1)
    print("Injected logic for phones loop")

# 2. Add /api/admin/chat/init endpoint before @app.post("/api/admin/enviar_mensaje")
target2 = r'@app.post("/api/admin/enviar_mensaje")'
replacement2 = r"""@app.post("/api/admin/chat/init")
async def init_chat(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    wa_id = data.get("wa_id", "").replace("+", "").replace(" ", "")
    if len(wa_id) > 6 and wa_id not in sesiones:
        sesiones[wa_id] = {
            "historial": [],
            "datos_pedido": {},
            "bot_activo": False,
            "ultima_actividad": datetime.utcnow()
        }
    return {"ok": True}

@app.post("/api/admin/enviar_mensaje")"""

if target2 in text:
    text = text.replace(target2, replacement2)
    print("Injected init route")
    
with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
    
# 3. Add context menu logic into inbox.html
with open("inbox.html", "r", encoding="utf-8") as f:
    inbox = f.read()

menu_html = """
    <!-- Phone Context Menu -->
    <div id="phoneContextMenu" style="display:none; position:fixed; background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:8px; padding:0.5rem; box-shadow:0 4px 15px rgba(0,0,0,0.5); z-index:10000; min-width:180px;">
        <div id="ctxPhoneTitle" style="font-size:0.75rem; color:var(--text-muted); padding:0.3rem 0.5rem; border-bottom:1px solid var(--accent-border); margin-bottom:0.3rem;">Teléfono</div>
        <button id="ctxPhoneChat" style="background:none; border:none; text-align:left; color:var(--text-main); font-size:0.85rem; padding:0.5rem; border-radius:4px; cursor:pointer; width:100%; display:flex; align-items:center; gap:0.5rem;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg> Iniciar Chat
        </button>
        <button id="ctxPhoneCopy" style="background:none; border:none; text-align:left; color:var(--text-main); font-size:0.85rem; padding:0.5rem; border-radius:4px; cursor:pointer; width:100%; display:flex; align-items:center; gap:0.5rem;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copiar Número
        </button>
    </div>

    <!-- Script para manejadores de teléfono -->
    <script>
        let targetPhoneCtx = "";
        function abrirCtxTelefono(e, phone) {
            e.preventDefault();
            e.stopPropagation();
            targetPhoneCtx = phone;

            let menu = document.getElementById('phoneContextMenu');
            document.getElementById('ctxPhoneTitle').innerText = "+" + phone;

            menu.style.display = 'block';
            let x = e.clientX;
            let y = e.clientY;
            if (x + menu.offsetWidth > window.innerWidth) x = window.innerWidth - menu.offsetWidth - 10;
            if (y + menu.offsetHeight > window.innerHeight) y = window.innerHeight - menu.offsetHeight - 10;
            menu.style.left = x + 'px';
            menu.style.top = y + 'px';
        }

        document.getElementById("ctxPhoneChat").addEventListener('click', async () => {
            document.getElementById('phoneContextMenu').style.display = 'none';
            const wa_id = targetPhoneCtx.replace(/\\D/g, '');
            if(wa_id.length > 6) {
                try {
                    await fetch('/api/admin/chat/init', { method: 'POST', body: JSON.stringify({wa_id}), headers:{'Content-Type':'application/json'} });
                } catch(e) {}
                window.location.href = "/inbox/" + wa_id;
            }
        });

        document.getElementById("ctxPhoneCopy").addEventListener('click', async () => {
            document.getElementById('phoneContextMenu').style.display = 'none';
            try {
                await navigator.clipboard.writeText("+" + targetPhoneCtx.replace(/\\D/g, ''));
            } catch(e) {}
        });

        document.addEventListener('click', () => {
            const m = document.getElementById('phoneContextMenu');
            if(m) m.style.display = 'none';
        });
    </script>
</body>"""

if "phoneContextMenu" not in inbox:
    inbox = inbox.replace("</body>", menu_html)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(inbox)
        print("Injected inbox.html JS")

import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = "from typing import Optional"
rep = """from typing import Optional

class InitChatPayload(BaseModel):
    wa_id: str

@app.post("/api/admin/chat/init")
async def api_init_chat(payload: InitChatPayload, request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    num_norm = normalizar_numero(payload.wa_id)
    obtener_o_crear_sesion(num_norm)
    return {"ok": True, "wa_id": num_norm}"""

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected init chat API")
else:
    print("Target not found server.py!")


with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target_html = """        document.getElementById("ctxPhoneChat").addEventListener('click', async () => {
            document.getElementById('phoneContextMenu').style.display = 'none';
            const wa_id = targetPhoneCtx.replace(/\D/g, '');
            if(wa_id.length > 6) {
                try {
                    await fetch('/api/admin/chat/init', { method: 'POST', body: JSON.stringify({wa_id}), headers:{'Content-Type':'application/json'} });
                } catch(e) {}
                window.location.href = "/inbox/" + wa_id;
            }
        });"""

rep_html = """        document.getElementById("ctxPhoneChat").addEventListener('click', async () => {
            document.getElementById('phoneContextMenu').style.display = 'none';
            const wa_id = targetPhoneCtx.replace(/\\D/g, '');
            if(wa_id.length > 6) {
                let final_wa_id = wa_id;
                try {
                    const res = await fetch('/api/admin/chat/init', { method: 'POST', body: JSON.stringify({wa_id}), headers:{'Content-Type':'application/json'} });
                    if(res.ok) {
                        const data = await res.json();
                        if(data.wa_id) final_wa_id = data.wa_id;
                    }
                } catch(e) {}
                window.location.href = "/inbox/" + final_wa_id;
            }
        });"""

if target_html in text:
    text = text.replace(target_html, rep_html)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected inbox.html JS")
else:
    print("Target not found inbox.html")

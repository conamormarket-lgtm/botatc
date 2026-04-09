import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add /api/admin/chat/init
target_init = r'@app.post("/api/admin/enviar_mensaje")'
replace_init = r"""@app.post("/api/admin/chat/init")
async def init_chat(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    wa_id = data.get("wa_id", "").replace("+", "").replace(" ", "")
    if len(wa_id) > 6 and wa_id not in sesiones:
        from datetime import datetime
        sesiones[wa_id] = {
            "historial": [],
            "datos_pedido": {},
            "bot_activo": False,
            "ultima_actividad": datetime.utcnow()
        }
    return {"ok": True}

@app.post("/api/admin/enviar_mensaje")"""

if target_init in text and "init_chat" not in text:
    text = text.replace(target_init, replace_init)
    print("Injected init route")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

# 2. Re-run inject_phone3.py which safely loop-injects the parser!
import subprocess
subprocess.run(["python", "inject_phone3.py"])

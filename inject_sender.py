import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = '''        for m in msgs:
            es_bot = m["role"] == "assistant"
            clase  = "bubble-bot" if es_bot else "bubble-user"
            lado   = "lado-der" if es_bot else "lado-izq"
            texto  = m["content"].replace("\\n", "<br>")'''

rep = '''        for m in msgs:
            es_bot = m["role"] == "assistant"
            clase  = "bubble-bot" if es_bot else "bubble-user"
            lado   = "lado-der" if es_bot else "lado-izq"
            texto  = m["content"].replace("\\n", "<br>")
            
            # Virtual group: Include visual author tag for user messages
            if not es_bot and "sender_name_override" in m:
                s_name = m.get("sender_name_override", "")
                s_waid = m.get("sender_wa_id", "")
                texto = f'<div style="background:rgba(255,255,255,0.08); padding:0.4rem 0.6rem; border-radius:4px; font-size:0.8rem; margin-bottom:0.4rem; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center;"><strong style="color:var(--text-main); font-family:var(--font-heading);">{s_name}</strong> <a href="/inbox/{s_waid}" style="color:var(--primary-color); text-decoration:none; font-weight:bold; padding:0.2rem 0.4rem; background:rgba(59, 130, 246, 0.15); border-radius:4px;">Responder ↗</a></div>' + texto'''

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected visual tag")
else:
    print("Target not found")

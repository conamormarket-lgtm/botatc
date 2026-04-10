import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

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

# Regex to safely replace inside `renderizar_inbox`
# We'll locate the string `load_all = request.query_params.get("history")` and search forward.
idx = text.find('load_all = request.query_params.get("history")')
if idx != -1:
    idx2 = text.find('        for m in msgs:', idx)
    if idx2 != -1:
        # find the end of texto definition
        idx3 = text.find('            def wrap_phone', idx2)
        if idx3 != -1:
            text = text[:idx2] + rep + '\n' + text[idx3:]
            with open("server.py", "w", encoding="utf-8") as f:
                f.write(text)
            print("Injected visual tag via manual indices")
        else:
            print("Error finding wrap_phone limit")
    else:
         print("Error finding for loop")
else:
    print("Error finding load_all")

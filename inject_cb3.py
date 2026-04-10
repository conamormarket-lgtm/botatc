import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

rep = '''        if s_fake_vg:
            chat_box = """<div style="padding:0.75rem; color:#c084fc; text-align:center; font-size:0.85rem; font-weight:600; display:flex; align-items:center; justify-content:center; gap:0.5rem;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg> GRUPO VIRTUAL DE SOLO LECTURA. HAGA CLIC EN EL LOGO DE UN MENSAJE PARA ABRIR SU CHAT PRIVADO.</div>"""
        elif activo_chat:'''

text = re.sub(r'\s+if activo_chat:', '\n' + rep, text, count=1)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Injected via RE")

import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = """        <div class="chat-input-area" """
rep = """        {grupo_virtual_banner}
        <div class="chat-input-area" {style_input_area} """

if target in text:
    text = text.replace(target, rep)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected inbox placeholders")
else:
    print("Target not found inbox")

with open("server.py", "r", encoding="utf-8") as f:
    text2 = f.read()

target2 = """    html = html.replace("{chat_viewer_html}", chat_viewer_html)"""
rep2 = """    html = html.replace("{chat_viewer_html}", chat_viewer_html)
    if s_fake_vg:
        html = html.replace("{style_input_area}", 'style="display:none;"')
        html = html.replace("{grupo_virtual_banner}", '''<div style="padding:0.75rem; background:rgba(168,85,247,0.1); border-top:1px solid rgba(168,85,247,0.3); color:#c084fc; text-align:center; font-size:0.85rem; font-weight:600;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:middle; margin-right:5px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg> GRUPO VIRTUAL DE SOLO LECTURA. HAZ CLIC EN EL LOGO/FOTO AL LADO DE UN MENSAJE PARA ABRIR SU CHAT PRIVADO.</div>''')
    else:
        html = html.replace("{style_input_area}", '')
        html = html.replace("{grupo_virtual_banner}", '')"""

if target2 in text2:
    text2 = text2.replace(target2, rep2)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text2)
    print("Injected python replacements")
else:
    print("Target not found server")


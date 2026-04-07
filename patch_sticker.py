import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement1 = '''
            texto_renderizado = texto_renderizado.replace("</div> | ", "</div><br>")
            
            # Formatear el indicador de respuesta nativa
'''
new_1 = '''
            texto_renderizado = texto_renderizado.replace("</div> | ", "</div><br>")
            
            if texto.startswith('[sticker') and texto.endswith(']'):
                clase += " bubble-sticker"
                
            # Formatear el indicador de respuesta nativa
'''

replacement2 = '''        .bubble-bot { background:var(--accent-bg); color:var(--text-main); border-bottom-left-radius:4px; border:1px solid var(--accent-border); }
        .bubble-user { background:var(--primary-color); color:#ffffff; border-bottom-right-radius:4px; }'''
new_2 = '''        .bubble-bot { background:var(--accent-bg); color:var(--text-main); border-bottom-left-radius:4px; border:1px solid var(--accent-border); }
        .bubble-user { background:var(--primary-color); color:#ffffff; border-bottom-right-radius:4px; }
        .bubble-sticker { background:transparent !important; border:none !important; padding:0 !important; box-shadow:none !important; }'''

if '.bubble-sticker {' not in text:
    text = text.replace(replacement2, new_2)
    text = text.replace(replacement1, new_1)
    
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("server.py updated")
else:
    print("already updated")

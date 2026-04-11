import re
import os

print("Empezando parcheo de firebase_client.py...")
with open("firebase_client.py", "r", encoding="utf-8") as f:
    fc = f.read()

if "def actualizar_preferencias_tema" not in fc:
    fc += """
def actualizar_preferencias_tema(username: str, preferencias_ui: dict) -> bool:
    db = inicializar_firebase()
    doc_ref = db.collection("usuarios_atc").document(username)
    if doc_ref.get().exists:
        doc_ref.update({"preferencias_ui": preferencias_ui})
        return True
    return False
"""
    with open("firebase_client.py", "w", encoding="utf-8") as f:
        f.write(fc)
    print("firebase_client.py parchado exitosamente.")
else:
    print("firebase_client.py ya tenia el metodo.")


print("Empezando parcheo de server.py...")
with open("server.py", "r", encoding="utf-8") as f:
    sc = f.read()

# 1. Agregar Endpoint
endpoint_str = """
@app.post("/api/user/theme")
async def update_user_theme(request: Request, bg_main: str = Form(None), accent_bg: str = Form(None), primary_color: str = Form(None), wallpaper: str = Form(None)):
    if not verificar_sesion(request):
        return {"ok": False, "error": "No autorizado"}
    
    usuario_sesion = obtener_usuario_sesion(request)
    if not usuario_sesion: return {"ok": False}
    
    prefs = {
        "bg_main": bg_main or "#213668",
        "accent_bg": accent_bg or "#ffffff",
        "primary_color": primary_color or "#3b82f6",
        "wallpaper": wallpaper or ""
    }
    
    username = usuario_sesion.get("username")
    if username:
        from firebase_client import actualizar_preferencias_tema
        actualizar_preferencias_tema(username, prefs)
        usuario_sesion["preferencias_ui"] = prefs
        save_sessions()
        
    return {"ok": True}
"""
if "@app.post(\"/api/user/theme\")" not in sc:
    # insert before @app.get("/inbox", response_class=HTMLResponse)
    sc = sc.replace('@app.get("/inbox", response_class=HTMLResponse)', endpoint_str + '\n@app.get("/inbox", response_class=HTMLResponse)')
    print("Endpoint /api/user/theme agregado.")

# 2. Inject {custom_theme_css} inside renderizar_inbox
inject_css_code = """
    # Tema Custom
    custom_theme_css = ""
    usuario_sesion = obtener_usuario_sesion(request)
    if usuario_sesion and "preferencias_ui" in usuario_sesion:
        prefs = usuario_sesion["preferencias_ui"]
        c_bg = prefs.get('bg_main', '#213668')
        c_prim = prefs.get('primary_color', '#3b82f6')
        c_acc = prefs.get('accent_bg', '#ffffff')
        
        # Parse hex to rgba for accent
        c_acc = c_acc.lstrip('#')
        if len(c_acc) == 6:
            c_acc_rgb = tuple(int(c_acc[i:i+2], 16) for i in (0, 2, 4))
            accent_bg_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.05)"
            accent_border_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.1)"
            accent_hover_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.08)"
        else:
            accent_bg_rgba = "rgba(255, 255, 255, 0.05)"
            accent_border_rgba = "rgba(255, 255, 255, 0.1)"
            accent_hover_rgba = "rgba(255, 255, 255, 0.08)"
            
        custom_theme_css = f'''
        :root {{
            --bg-main: {c_bg} !important;
            --bg-sidebar: {c_bg} !important;
            --bg-list: {c_bg} !important;
            --primary-color: {c_prim} !important;
            --accent-bg: {accent_bg_rgba} !important;
            --accent-border: {accent_border_rgba} !important;
            --accent-hover-soft: {accent_hover_rgba} !important;
        }}
        '''
        wp = prefs.get('wallpaper', '')
        if wp:
            custom_theme_css += f'''
            .chat-viewer-panel {{
                background-image: url('{wp}') !important;
                background-size: cover !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
            }}
            .empty-state {{
                background: rgba(0,0,0,0.4) !important;
                border-radius: 12px;
                backdrop-filter: blur(5px);
            }}
            '''

    html = html.replace("{custom_theme_css}", custom_theme_css)
"""

if "{custom_theme_css}" not in sc:
    # find: html = html.replace("{chat_view_css}", chat_view_css)
    if 'html = html.replace("{chat_view_css}", chat_view_css)' in sc:
        sc = sc.replace('html = html.replace("{chat_view_css}", chat_view_css)', 
                        'html = html.replace("{chat_view_css}", chat_view_css)\n' + inject_css_code)
        print("CSS injertado en server.py localizadamente.")
    else:
        print("No se halló html = html.replace(\"{chat_view_css}\", chat_view_css) en server.py.")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(sc)

print("Parcheo de server.py terminado.")


print("Empezando parcheo de inbox.html...")
with open("inbox.html", "r", encoding="utf-8") as f:
    ic = f.read()
    
if "{custom_theme_css}" not in ic:
   ic = ic.replace("</style>\n</head>", "</style>\n<style id=\"custom-theme-css\">\n{custom_theme_css}\n</style>\n</head>")
   print("Añadido hook css en inbox.html")
else:
   print("inbox.html ya tiene el css hook")
   
with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(ic)

print("Todo listo.")

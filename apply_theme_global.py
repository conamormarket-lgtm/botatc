import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

helper_function = """
def inyectar_tema_global(request, html: str) -> str:
    \"\"\"Inyecta dinámicamente las preferencias visuales del usuario en todas las respuestas HTML\"\"\"
    usuario_sesion = obtener_usuario_sesion(request)
    prefs = usuario_sesion.get("preferencias_ui", {}) if usuario_sesion else {}
    c_bg = prefs.get('bg_main', '#0f172a')
    c_prim = prefs.get('primary_color', '#3b82f6')
    c_acc = prefs.get('accent_bg', '#1e293b')
    wp = prefs.get('wallpaper', '')

    c_acc_hex = c_acc.lstrip('#')
    if len(c_acc_hex) == 6:
        c_acc_rgb = tuple(int(c_acc_hex[i:i+2], 16) for i in (0, 2, 4))
        accent_bg_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.05)"
        accent_border_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.1)"
        accent_hover_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.08)"
    else:
        accent_bg_rgba = "rgba(255, 255, 255, 0.05)"
        accent_border_rgba = "rgba(255, 255, 255, 0.1)"
        accent_hover_rgba = "rgba(255, 255, 255, 0.08)"

    css = f'''
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
    
    if wp:
        css += f'''
        .chat-viewer-panel, .settings-main-panel, body {{
            background-image: url('{wp}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        .appearance-card, .proactive-card, .pdf-card, .backup-card {{
            background: rgba(30, 41, 59, 0.85) !important;
            backdrop-filter: blur(10px);
        }}
        '''

    # Si la template tiene lugar para {custom_theme_css}, insertalo. 
    # Sino, mételo antes de cerrar </head>
    if "{custom_theme_css}" in html:
        html = html.replace("{custom_theme_css}", css)
    elif "</head>" in html:
        html = html.replace("</head>", f"<style id='custom-theme-css'>{css}</style></head>")
        
    # Reemplazar placeholders extra si existen (para el perfil form)
    html = html.replace("{bg_main}", c_bg)
    html = html.replace("{primary_color}", c_prim)
    html = html.replace("{accent_bg}", c_acc)
    html = html.replace("{wallpaper}", wp)
    return html
"""

if "def inyectar_tema_global(" not in code:
    code = code.replace("app = FastAPI()", "app = FastAPI()\n\n" + helper_function)

# Reemplazar los returns para que pasen por inyectar_tema_global
# 1. En settings_panel
code = re.sub(r'return HTMLResponse\(html\)', r'return HTMLResponse(inyectar_tema_global(request, html))', code)

# Borrar la vieja inyeccion repetitiva en perfil_panel y renderizar_inbox
# We'll just carefully strip it
bad_code_perfil = """    # Inyectar CSS dinámico exacto al de inbox
    custom_theme_css = ""
    c_bg = prefs.get('bg_main', '#0f172a')
    c_prim = prefs.get('primary_color', '#3b82f6')
    c_acc = prefs.get('accent_bg', '#1e293b')
    c_acc_hex = c_acc.lstrip('#')
    if len(c_acc_hex) == 6:
        c_acc_rgb = tuple(int(c_acc_hex[i:i+2], 16) for i in (0, 2, 4))
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
        .settings-main-panel {{
            background-image: url('{wp}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        .appearance-card {{
            background: rgba(30, 41, 59, 0.85) !important;
            backdrop-filter: blur(10px);
        }}
        '''

    html = html.replace("{custom_theme_css}", custom_theme_css)
    html = html.replace("{bg_main}", c_bg)
    html = html.replace("{primary_color}", c_prim)
    html = html.replace("{accent_bg}", c_acc)
    html = html.replace("{wallpaper}", wp)"""

bad_code_inbox = """    # Tema Custom
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

    html = html.replace("{custom_theme_css}", custom_theme_css)"""

code = code.replace(bad_code_perfil, "")
code = code.replace(bad_code_inbox, "")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
    
print("Patch OK")

import sys
sys.path.insert(0, '.')

# Simular la llamada a inyectar_tema_global con un request falso
class FakePrefs:
    def get(self, k, d):
        prefs = {
            'bg_main': '#000000',
            'primary_color': '#717f7f',
            'accent_bg': '#ffffff',
            'text_main': '#f8fafc',
            'text_muted': '#94a3b8',
            'font_heading': 'Plus Jakarta Sans',
            'font_main': 'Inter',
            'nav_position': 'top',
            'wallpaper': '/api/media/wallpaper/wp_admin_1777084859.jpeg',
            'wallpaper_opacity': '1.0',
            'wallpaper_offset_y': '50',
            'wallpaper_offset_x': '50',
        }
        return prefs.get(k, d)

class FakeSession:
    def get(self, k, d=None):
        if k == 'preferencias_ui':
            return FakePrefs()
        return d

class FakeRequest:
    cookies = {'session_token': 'fake'}

# Leer el HTML de admin.html
with open('admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Reemplazar placeholders basicos
html = html.replace('{main_nav_html}', '<nav>NAV</nav>')
html = html.replace('{color_global}', '#10b981')
html = html.replace('{class_btn_toggle}', '')
html = html.replace('{txt_btn_toggle}', 'Toggle IA')
html = html.replace('{custom_theme_css}', '')

# Simular la generacion del CSS de inyectar_tema_global
c_bg = '#000000'
c_prim = '#717f7f'
c_acc = '#ffffff'
wp = '/api/media/wallpaper/wp_admin_1777084859.jpeg'
wp_opacity = 1.0
t_main = '#f8fafc'
t_muted = '#94a3b8'

c_acc_hex = c_acc.lstrip('#')
c_acc_rgb = tuple(int(c_acc_hex[i:i+2], 16) for i in (0, 2, 4))
accent_bg_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.05)"
accent_border_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.1)"

print("accent_bg que se inyecta en :root:", accent_bg_rgba)

# Ver el CSS que se genera
css_snippet = f"""
:root {{
    --accent-bg: {accent_bg_rgba} !important;
    --accent-border: {accent_border_rgba} !important;
}}
.appearance-card, .proactive-card, .pdf-card, .backup-card, .editor-card,
.stat-card, .table-card, .qr-card {{
    background: var(--accent-bg) !important;
    border: 1px solid var(--accent-border) !important;
}}
"""
print()
print("=== CSS que se inyecta ===")
print(css_snippet)

# Verificar si el html tiene </head>
print("¿Tiene </head>?", '</head>' in html)
print("¿Tiene {custom_theme_css}?", '{custom_theme_css}' in html)

import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""            texto = re.sub(r"\[(sticker-local|sticker|imagen|audio|video):([^\]]+)\]", reemplazar_archivos_inline, texto)"""

replacement = r"""            texto = re.sub(r"\[(sticker-local|sticker|imagen|audio|video):([^\]]+)\]", reemplazar_archivos_inline, texto)

            def reemplazar_ubicacion(match):
                coords_str = match.group(1)
                partes = coords_str.split(",", 2)
                lat, lon = partes[0], partes[1]
                addr = partes[2] if len(partes) > 2 else ""
                maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                addr_text = f"<br><span style='font-size:0.7rem;opacity:0.8'>{addr}</span>" if addr else ""
                return f'<div style="text-align:center; margin-bottom: 4px;"><a href="{maps_url}" target="_blank" style="display:inline-block; background:rgba(255,255,255,0.1); padding:0.5rem 1rem; border-radius:8px; color:var(--text-main); text-decoration:none; border:1px solid var(--accent-border); font-size:0.85rem;">📍 <span style="text-decoration:underline;">Ver Ubicación en Google Maps</span>{addr_text}</a></div>'

            texto = re.sub(r"\[ubicacion:([^\]]+)\]", reemplazar_ubicacion, texto)"""

if target in text:
    text = text.replace(target, replacement)
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replace success")
else:
    print("Target not found")

import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'            texto = re\.sub\(r"\\\[\(sticker-local.*?reemplazar_archivos_inline, texto\)', text, flags=re.DOTALL)
if m:
    target = m.group(0)
    replacement = target + """

            def reemplazar_ubicacion(match):
                coords_str = match.group(1)
                partes = coords_str.split(",", 2)
                lat, lon = partes[0], partes[1]
                addr = partes[2] if len(partes) > 2 else ""
                maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                addr_text = f"<br><span style='font-size:0.75rem;opacity:0.8'>📍 {addr}</span>" if addr else ""
                return f'<div style="text-align:center; margin-bottom: 4px;"><a href="{maps_url}" target="_blank" style="display:inline-block; background:rgba(255,255,255,0.05); padding:0.6rem 1rem; border-radius:12px; color:var(--text-main); text-decoration:none; border:1px solid var(--accent-border); font-size:0.85rem;">🗺️ <span style="text-decoration:underline;">Ver Ubicación de WhatsApp en Google Maps</span>{addr_text}</a></div>'

            texto = re.sub(r"\[ubicacion:([^\]]+)\]", reemplazar_ubicacion, texto)"""
            
    text = text.replace(target, replacement)
    
    # Also I must modify recibir_mensaje
    m2 = re.search(r'        elif tipo_mensaje == "document":.*?texto_cliente = f"\[📎 Archivo: \{filename\}\]"\n', text, flags=re.DOTALL)
    if m2:
        target2 = m2.group(0)
        replacement2 = target2 + """        elif tipo_mensaje == "location":
            lat = mensaje_data.get("location", {}).get("latitude", "")
            lon = mensaje_data.get("location", {}).get("longitude", "")
            addr = mensaje_data.get("location", {}).get("address", "")
            texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
"""
        text = text.replace(target2, replacement2)
        print("Replaced both")
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
else:
    print("UI replace target not found")

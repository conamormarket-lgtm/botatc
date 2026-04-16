import re, urllib.parse

def patch_server():
    with open('server.py', 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Search scroll target and load_all
    text = text.replace(
        'if "msg_id" in request.query_params:\n            msgId_target = request.query_params["msg_id"]',
        'if "msg_id" in request.query_params:\n            load_all = True\n            msgId_target = request.query_params["msg_id"]'
    )

    t_re = re.sub(
        r"// Deslizarse automáticamente al mensaje.*?\}\n",
        r'''// Deslizarse automáticamente al mensaje buscado con múltiples reintentos
            if (msgId_target) {
                window._isSearching = true; // Desactivar auto-scroll hacia abajo temporalmente
                
                const scrollToMsg = () => {
                    const el = document.getElementById('msg-' + msgId_target);
                    if (el) {
                        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        el.style.transition = 'box-shadow 0.5s ease';
                        el.style.boxShadow = '0 0 15px var(--primary-color)';
                        setTimeout(() => el.style.boxShadow = 'none', 3000);
                        return true;
                    }
                    return false;
                };

                // Intentar deslizar inmediatamente
                if (!scrollToMsg()) {
                    // Reintentar en 600ms (después de cargar DOM)
                    setTimeout(() => {
                        if (!scrollToMsg()) {
                            // Reintentar en 1500ms (después de cargar imágenes)
                            setTimeout(scrollToMsg, 1500);
                        }
                    }, 600);
                }
                
                // Restablecer el polling regular de scroll después de 3 segundos
                setTimeout(() => { window._isSearching = false; }, 3000);
            }
''', text, flags=re.DOTALL
    )
    if t_re != text: text = t_re

    # 2. Add Caption support regex inside renderizar_inbox
    t_re2 = re.sub(
        r'''            def reemplazar_archivos_inline\(match\):.*?elif tipo == "audio":''',
        r'''            def reemplazar_archivos_inline(match):
                tipo = match.group(1)
                media_id_raw = match.group(2)
                
                caption = None
                import urllib.parse
                if "|caption:" in media_id_raw:
                    parts = media_id_raw.split("|caption:", 1)
                    media_id = parts[0]
                    caption = urllib.parse.unquote(parts[1])
                else:
                    media_id = media_id_raw
                
                caption_html = f'<div style="font-size:0.85rem; padding:6px; max-width:350px; margin:0 auto; background:rgba(0,0,0,0.3); border-bottom-left-radius:8px; border-bottom-right-radius:8px; color:var(--text-main); word-break:break-word; border:1px solid rgba(255,255,255,0.05); border-top:none; margin-top:-5px; box-sizing:border-box;">{caption.replace("<", "&lt;").replace(">", "&gt;")}</div>' if caption else ""
                
                if tipo == "sticker-local":
                    src_url = f"/api/media/sticker/{media_id}"
                    return f'<div style="text-align:center;"><img src="{src_url}" style="width: 150px; height: 150px; object-fit: contain; border-radius: 8px; background: transparent; margin-bottom: 5px; display:inline-block;" alt="Sticker Local {media_id}"></div>'
                    
                src_url = media_id if media_id.startswith("http") else f"/api/media/{media_id}"
                
                if tipo == "sticker":
                    return f'<div style="text-align:center;"><img src="{src_url}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display:inline-block;" alt="Sticker {media_id}" onerror="this.onerror=null; this.src=\'https://placehold.co/150x150?text=Sticker\';"></div>'
                elif tipo == "imagen":
                    res = f'<div style="text-align:center; max-width: 350px; margin: 0 auto;"><img src="{src_url}" style="max-width: 100%; max-height: 350px; width: auto; object-fit: contain; border-radius: 8px; {"border-bottom-left-radius:0; border-bottom-right-radius:0;" if caption else ""} background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src=\'https://placehold.co/250x150?text=Imagen\';"></div>'
                    return res + caption_html
                elif tipo == "video":
                    res = f'<div style="text-align:center; max-width: 350px; margin: 0 auto;"><video controls src="{src_url}" style="max-width: 100%; max-height: 350px; width: auto; object-fit: contain; border-radius: 8px; {"border-bottom-left-radius:0; border-bottom-right-radius:0;" if caption else ""} background: rgba(0,0,0,0.6); margin-bottom: 5px; display: block; margin: 0 auto;"></video></div>'
                    return res + caption_html
                elif tipo == "audio":''',
        text, flags=re.DOTALL
    )
    if t_re2 != text: text = t_re2

    # 3. Add Caption parsing to enviar_manual using regex substitution
    t_re3 = re.sub(
        r'''partes = re.split.*?match_sticker_local = re.match.*?w_id_current = None.*?if match_sticker:.*?elif match_audio:''',
        r'''partes = re.split(r'(\[(?:sticker|imagen|video|audio|sticker-local|documento):[^\]]+\])', texto)
            
            for p in partes:
                p = p.strip()
                if not p: continue
                
                match_sticker = re.match(r"^\[sticker:([^\|\]]+)\]$", p)
                match_img = re.match(r"^\[imagen:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
                match_video = re.match(r"^\[video:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
                match_audio = re.match(r"^\[audio:([^\|\]]+)\]$", p)
                match_doc = re.match(r"^\[documento:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
                match_sticker_local = re.match(r"^\[sticker-local:([^\|\]]+)\]$", p)
                
                w_id_current = None
                try:
                    import urllib.parse
                    if match_sticker: 
                        w_id_current = enviar_media(target, "sticker", match_sticker.group(1))
                    elif match_img:
                        cap = urllib.parse.unquote(match_img.group(2)) if match_img.group(2) else None
                        w_id_current = enviar_media(target, "image", match_img.group(1), caption=cap)
                    elif match_video:
                        cap = urllib.parse.unquote(match_video.group(2)) if match_video.group(2) else None
                        w_id_current = enviar_media(target, "video", match_video.group(1), caption=cap)
                    elif match_doc:
                        cap = urllib.parse.unquote(match_doc.group(2)) if match_doc.group(2) else None
                        w_id_current = enviar_media(target, "document", match_doc.group(1), caption=cap)
                    elif match_audio:''',
        text, flags=re.DOTALL, count=1
    )
    if t_re3 != text: text = t_re3

    t_re4 = re.sub(
        r'''partes = re.split.*?for p in partes:.*?match_sticker = re.match.*?w_id_current = None.*?if match_sticker:.*?elif match_audio:''',
        r'''partes = re.split(r'(\[(?:sticker|imagen|video|audio|sticker-local|documento):[^\]]+\])', texto)
        last_wamid = None
        exito_alguna_parte = False
        
        for p in partes:
            p = p.strip()
            if not p: continue
            
            match_sticker = re.match(r"^\[sticker:([^\|\]]+)\]$", p)
            match_img = re.match(r"^\[imagen:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
            match_video = re.match(r"^\[video:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
            match_audio = re.match(r"^\[audio:([^\|\]]+)\]$", p)
            match_doc = re.match(r"^\[documento:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
            match_sticker_local = re.match(r"^\[sticker-local:([^\|\]]+)\]$", p)
            
            w_id_current = None
            try:
                import urllib.parse
                if match_sticker: 
                    w_id_current = enviar_media(wa_id, "sticker", match_sticker.group(1), reply_to_wamid)
                elif match_img:
                    cap = urllib.parse.unquote(match_img.group(2)) if match_img.group(2) else None
                    w_id_current = enviar_media(wa_id, "image", match_img.group(1), reply_to_wamid, caption=cap)
                elif match_video:
                    cap = urllib.parse.unquote(match_video.group(2)) if match_video.group(2) else None
                    w_id_current = enviar_media(wa_id, "video", match_video.group(1), reply_to_wamid, caption=cap)
                elif match_doc:
                    cap = urllib.parse.unquote(match_doc.group(2)) if match_doc.group(2) else None
                    w_id_current = enviar_media(wa_id, "document", match_doc.group(1), reply_to_wamid, caption=cap)
                elif match_audio:''',
        text, flags=re.DOTALL, count=1
    )
    if t_re4 != text: text = t_re4

    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(text)

def patch_whatsapp():
    with open('whatsapp_client.py', 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace(
        'def enviar_media(numero_destino: str, tipo_media: str, media_id_o_url: str, reply_to_wamid: str = None) -> bool:\n',
        'def enviar_media(numero_destino: str, tipo_media: str, media_id_o_url: str, reply_to_wamid: str = None, caption: str = None) -> bool:\n'
    )
    c = c.replace(
        'if tipo_media == "audio":\n        media_obj["voice"] = True\n',
        'if tipo_media == "audio":\n        media_obj["voice"] = True\n    if caption and tipo_media in ["image", "video", "document"]:\n        media_obj["caption"] = caption\n'
    )
    with open('whatsapp_client.py', 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == '__main__':
    patch_server()
    patch_whatsapp()

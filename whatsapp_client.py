# ============================================================
#  whatsapp_client.py — Envía mensajes a WhatsApp via Meta Cloud API
# ============================================================
#  ⚠️  IMPORTANTE: Este módulo es EXCLUSIVAMENTE para Meta Cloud API.
#  Para líneas QR/Baileys, usar qr_client.py.
#  El único punto donde se toca QR aquí es el ROUTER (if line_id.startswith).
# ============================================================
import httpx
from config import META_ACCESS_TOKEN, META_PHONE_NUMBER_ID, META_API_VERSION

def _get_line_id(numero: str, override_line_id: str) -> str:
    """Extrae dinámicamente el lineId del contexto en memoria del servidor."""
    if override_line_id != "principal":
        return override_line_id
    import sys
    svr = sys.modules.get('server') or sys.modules.get('__main__')
    if svr and hasattr(svr, 'sesiones'):
        ses = svr.sesiones.get(numero)
        if ses:
            return ses.get('lineId', 'principal')
    return "principal"

def _get_meta_credentials(line_id: str) -> tuple[str, str, str]:
    """Retorna (token, phone_id, api_url) leyendo la configuración dinámica de la línea."""
    import os
    import json
    token = META_ACCESS_TOKEN
    phone_id = META_PHONE_NUMBER_ID
    
    try:
        if line_id != "principal" and os.path.exists("line_aliases.json"):
            with open("line_aliases.json", "r") as f:
                aliases = json.load(f)
            linfo = aliases.get(line_id, {})
            if isinstance(linfo, dict):
                if linfo.get("meta_token"):
                    token = linfo["meta_token"]
                if linfo.get("meta_phone_id"):
                    phone_id = linfo["meta_phone_id"]
    except Exception as e:
        print(f"[WARN] No se pudo leer credencial de Meta para línea {line_id}: {e}")
        
    url = f"https://graph.facebook.com/{META_API_VERSION}/{phone_id}/messages"
    return token, phone_id, url


def enviar_mensaje(numero_destino: str, texto: str, reply_to_wamid: str = None, line_id: str = "principal") -> bool:
    """
    Envía un mensaje de texto. Ruteador: QR → qr_client | Meta → Graph API.
    """
    line_id = _get_line_id(numero_destino, line_id)
    if line_id.startswith("qr_"):                                   # ← ROUTER QR
        from qr_client import enviar_mensaje_qr                     # ← ROUTER QR
        return enviar_mensaje_qr(numero_destino, texto, reply_to_wamid, line_id)

    meta_token, meta_phone_id, meta_api_url = _get_meta_credentials(line_id)

    headers = {
        "Authorization": f"Bearer {meta_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto},
    }
    
    if reply_to_wamid:
        payload["context"] = {"message_id": reply_to_wamid}

    try:
        response = httpx.post(meta_api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Error Meta API ({e.response.status_code}): {e.response.text}")
        return None
    except Exception as e:
        print(f"[ERROR] Error enviando mensaje: {e}")
        return None

def enviar_media(numero_destino: str, tipo_media: str, media_id_o_url: str, reply_to_wamid: str = None, caption: str = None, line_id: str = "principal") -> bool:
    """
    Envía media. Ruteador: QR → qr_client | Meta → Graph API.
    tipo_media: 'sticker', 'image', 'video', 'audio', 'document'
    """
    line_id = _get_line_id(numero_destino, line_id)
    if line_id.startswith("qr_"):                                   # ← ROUTER QR
        from qr_client import enviar_media_qr                       # ← ROUTER QR
        return enviar_media_qr(numero_destino, tipo_media, media_id_o_url, reply_to_wamid, caption, line_id)

    meta_token, meta_phone_id, meta_api_url = _get_meta_credentials(line_id)

    headers = {
        "Authorization": f"Bearer {meta_token}",
        "Content-Type": "application/json",
    }
    
    es_url = media_id_o_url.startswith("http")
    media_obj = {"link": media_id_o_url} if es_url else {"id": media_id_o_url}
    
    if tipo_media == "audio":
        media_obj["voice"] = True
    
    if caption and tipo_media in ['image', 'video', 'document']:
        media_obj["caption"] = caption
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": tipo_media,
        tipo_media: media_obj,
    }
    
    if reply_to_wamid:
        payload["context"] = {"message_id": reply_to_wamid}

    try:
        response = httpx.post(meta_api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        err_msg = e.response.text
        print(f"[ERROR] Error Meta API ({e.response.status_code}): {err_msg}")
        return f"ERROR_META: {err_msg}"
    except Exception as e:
        print(f"[ERROR] Error enviando media ({tipo_media}): {e}")
        return None


async def enviar_mensaje_texto(numero_destino: str, texto: str, line_id: str = "principal") -> bool:
    """
    Versión async de enviar_mensaje. Ruteador: QR → qr_client | Meta → Graph API.
    """
    line_id = _get_line_id(numero_destino, line_id)
    if line_id.startswith("qr_"):                                   # ← ROUTER QR
        from qr_client import enviar_mensaje_qr_async               # ← ROUTER QR
        return await enviar_mensaje_qr_async(numero_destino, texto, None, line_id)

    meta_token, meta_phone_id, meta_api_url = _get_meta_credentials(line_id)

    headers = {
        "Authorization": f"Bearer {meta_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto},
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(meta_api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            print(f"[OK] Mensaje manual enviado a {numero_destino}")
            return response.json().get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Error Meta API al enviar manual ({e.response.status_code}): {e.response.text}")
        return None
    except Exception as e:
        print(f"[ERROR] Error enviando mensaje manual: {e}")
        return None


async def obtener_media_url(media_id: str) -> str | None:
    """Consigue la URL temporal de descarga de un media_id de Meta o retorna la URL cruda si es local (QR)."""
    if media_id.startswith("http"):
        return media_id

    url = f"https://graph.facebook.com/{META_API_VERSION}/{media_id}"
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json().get("url")
    except Exception as e:
        print(f"[ERROR] Error al obtener URL de media {media_id}: {e}")
        return None


async def descargar_media(media_url: str) -> tuple[bytes | None, str | None]:
    """Descarga el binario de la foto o sticker y su tipo MIME usando el token de Meta o sin token si es local."""
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(media_url, headers=headers, timeout=15)
            res.raise_for_status()
            mime_type = res.headers.get("content-type")
            return res.content, mime_type
    except Exception as e:
        print(f"[ERROR] Error descargando media: {e}")
        return None, None

async def subir_media(file_bytes: bytes, mime_type: str, filename: str = "upload.png") -> str | None:
    """Sube un archivo binario a Meta Graph API y retorna su Media ID nativo."""
    url = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    files = {"file": (filename, file_bytes, mime_type)}
    data = {"messaging_product": "whatsapp"}
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, data=data, files=files, timeout=120)
            res.raise_for_status()
            return res.json().get("id")
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Error HTTP subiendo media ({e.response.status_code}): {e.response.text}")
        return f"ERROR_META:{e.response.text}"
    except Exception as e:
        print(f"[ERROR] Error subiendo media a Meta: {e}")
        return f"ERROR_META:{str(e)}"

async def enviar_reaccion_async(numero_destino: str, message_id: str, emoji: str, line_id: str = "principal") -> bool:
    """Envía una reacción. Ruteador: QR → qr_client | Meta → Graph API."""
    line_id = _get_line_id(numero_destino, line_id)
    if line_id.startswith("qr_"):                                   # ← ROUTER QR
        from qr_client import enviar_reaccion_qr                    # ← ROUTER QR
        return await enviar_reaccion_qr(numero_destino, message_id, emoji, line_id)
    meta_token, meta_phone_id, meta_api_url = _get_meta_credentials(line_id)

    headers = {
        "Authorization": f"Bearer {meta_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "reaction",
        "reaction": {
            "message_id": message_id,
            "emoji": emoji
        }
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(meta_api_url, headers=headers, json=payload, timeout=10)
            res.raise_for_status()
            return True
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Error Meta Reaccion ({e.response.status_code}): {e.response.text}")
        return False
    except Exception as e:
        print(f"[ERROR] Error enviando reacción: {e}")
        return False


async def enviar_plantilla(numero_destino: str, template_name: str, language_code: str = "es", components: list = None, line_id: str = "principal") -> str | None:
    """Envía un Message Template preaprobado por Meta. QR no soporta plantillas."""
    line_id = _get_line_id(numero_destino, line_id)
    if line_id.startswith("qr_"):                                   # ← ROUTER QR
        # Las plantillas de Meta no aplican a líneas QR — texto de aviso
        txt = f"[Plantilla '{template_name}' solicitada — no compatible con canal QR.]"
        from qr_client import enviar_mensaje_qr_async               # ← ROUTER QR
        return await enviar_mensaje_qr_async(numero_destino, txt, None, line_id)

    meta_token, meta_phone_id, meta_api_url = _get_meta_credentials(line_id)

    headers = {
        "Authorization": f"Bearer {meta_token}",
        "Content-Type": "application/json",
    }
    
    template_data = {
        "name": template_name,
        "language": {"code": language_code}
    }
    
    
    if components is not None:
        if len(components) > 0 and isinstance(components[0], str):
            # Se pasaron parametros simples (texto)
            structured_params = [{"type": "text", "text": str(c)} for c in components]
            template_data["components"] = [{
                "type": "body",
                "parameters": structured_params
            }]
        else:
            # Se paso la estructura compleja
            template_data["components"] = components

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destino,
        "type": "template",
        "template": template_data
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(meta_api_url, headers=headers, json=payload, timeout=10)
            res.raise_for_status()
            data = res.json()
            return data.get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] Error Meta Plantilla ({e.response.status_code}): {e.response.text}")
        return None
    except Exception as e:
        print(f"[ERROR] Error enviando plantilla: {e}")
        return None

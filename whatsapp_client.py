# ============================================================
#  whatsapp_client.py — Envía mensajes a WhatsApp via Meta API
# ============================================================
import httpx
from config import META_ACCESS_TOKEN, META_PHONE_NUMBER_ID, META_API_VERSION

META_API_URL = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/messages"


def enviar_mensaje(numero_destino: str, texto: str, reply_to_wamid: str = None) -> bool:
    """
    Envía un mensaje de texto al número de WhatsApp indicado.

    Args:
        numero_destino: Número completo con código de país (ej: '51945257117')
        texto:          Texto del mensaje a enviar

    Returns:
        wamid string si el envío fue exitoso, None si hubo error.
    """
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
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
        response = httpx.post(META_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        print(f"❌ Error Meta API ({e.response.status_code}): {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return None

def enviar_media(numero_destino: str, tipo_media: str, media_id_o_url: str, reply_to_wamid: str = None) -> bool:
    """
    Envía media (sticker, imagen, video, documento) a un número.
    tipo_media: 'sticker', 'image', 'video', 'audio', 'document'
    """
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    
    es_url = media_id_o_url.startswith("http")
    media_obj = {"link": media_id_o_url} if es_url else {"id": media_id_o_url}
    
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
        response = httpx.post(META_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        print(f"❌ Error Meta API ({e.response.status_code}): {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error enviando media ({tipo_media}): {e}")
        return None


async def enviar_mensaje_texto(numero_destino: str, texto: str) -> bool:
    """
    Versión async de enviar_mensaje para usar desde endpoints FastAPI.
    Usa httpx.AsyncClient para no bloquear el event loop.
    """
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
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
            response = await client.post(META_API_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✅ Mensaje manual enviado a {numero_destino}")
            return response.json().get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        print(f"❌ Error Meta API al enviar manual ({e.response.status_code}): {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error enviando mensaje manual: {e}")
        return None


async def obtener_media_url(media_id: str) -> str | None:
    """Consigue la URL temporal de descarga de un media_id de Meta."""
    url = f"https://graph.facebook.com/{META_API_VERSION}/{media_id}"
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json().get("url")
    except Exception as e:
        print(f"❌ Error al obtener URL de media {media_id}: {e}")
        return None


async def descargar_media(media_url: str) -> tuple[bytes | None, str | None]:
    """Descarga el binario de la foto o sticker y su tipo MIME usando el token de Meta."""
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(media_url, headers=headers, timeout=15)
            res.raise_for_status()
            mime_type = res.headers.get("content-type")
            return res.content, mime_type
    except Exception as e:
        print(f"❌ Error descargando media: {e}")
        return None, None

async def subir_media(file_bytes: bytes, mime_type: str, filename: str = "upload.png") -> str | None:
    """Sube un archivo binario a Meta Graph API y retorna su Media ID nativo."""
    url = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    files = {"file": (filename, file_bytes, mime_type)}
    data = {"messaging_product": "whatsapp"}
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, data=data, files=files, timeout=30)
            res.raise_for_status()
            return res.json().get("id")
    except httpx.HTTPStatusError as e:
        print(f"❌ Error HTTP subiendo media ({e.response.status_code}): {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error subiendo media a Meta: {e}")
        return None

async def enviar_reaccion_async(numero_destino: str, message_id: str, emoji: str) -> bool:
    """Envía una reacción a un mensaje específico."""
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
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
            res = await client.post(META_API_URL, headers=headers, json=payload, timeout=10)
            res.raise_for_status()
            return True
    except httpx.HTTPStatusError as e:
        print(f"❌ Error Meta Reaccion ({e.response.status_code}): {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error enviando reacción: {e}")
        return False

# ============================================================
#  qr_client.py — Operaciones de WhatsApp vía Baileys / QR
# ============================================================
#  IMPORTANTE: Este módulo es 100% independiente de whatsapp_client.py
#  y de la Meta Cloud API. NUNCA llamar a Graph API desde aquí.
#  Todo tráfico va a http://localhost:3000 (microservicio Node.js Baileys).
# ============================================================

import json
import urllib.request
import urllib.error

QR_SERVICE_URL = "http://localhost:3000"
QR_TIMEOUT = 6.0

# ────────────────────────────────────────────────────────────
# Helpers internos
# ────────────────────────────────────────────────────────────

def _post(endpoint: str, payload: dict) -> dict | None:
    """HTTP POST sin dependencias externas al microservicio Node.js."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{QR_SERVICE_URL}{endpoint}",
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "qr_client/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=QR_TIMEOUT) as res:
            return json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"[QR_CLIENT] [ERROR] HTTP {e.code} en {endpoint}: {body}")
        return {}
    except Exception as e:
        print(f"[QR_CLIENT] [ERROR] Error en POST {endpoint}: {e}")
        return {}


def _get(endpoint: str) -> dict | None:
    """HTTP GET sin dependencias externas al microservicio Node.js."""
    req = urllib.request.Request(
        f"{QR_SERVICE_URL}{endpoint}",
        headers={"User-Agent": "qr_client/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=QR_TIMEOUT) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        print(f"[QR_CLIENT] [ERROR] Error en GET {endpoint}: {e}")
        return {}


def _get_bytes(endpoint: str) -> tuple[bytes | None, str | None]:
    """HTTP GET que devuelve los bytes crudos (para media) y el mime_type."""
    req = urllib.request.Request(
        f"{QR_SERVICE_URL}{endpoint}",
        headers={"User-Agent": "qr_client/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=QR_TIMEOUT) as res:
            mime = res.headers.get("Content-Type", "application/octet-stream")
            return res.read(), mime
    except Exception as e:
        print(f"[QR_CLIENT] [ERROR] Error descargando bytes de {endpoint}: {e}")
        return None, None


# ────────────────────────────────────────────────────────────
# Envío de texto
# ────────────────────────────────────────────────────────────

def enviar_mensaje_qr(
    numero_destino: str,
    texto: str,
    reply_to_wamid: str = None,
    line_id: str = "qr_ventas_1",
) -> str | None:
    """
    Envía texto al cliente vía Baileys.
    Retorna el msg_id de Baileys si tuvo éxito, None si falló.
    """
    result = _post("/api/qr/send", {
        "to": numero_destino,
        "text": texto,
    })
    if result and result.get("status") == "ok":
        msg_id = result.get("id")
        print(f"[QR_CLIENT] [OK] Texto enviado a {numero_destino} (id: {msg_id})")
        import uuid
        return msg_id if msg_id else f"qr_text_sent_{uuid.uuid4().hex[:8]}"
    print(f"[QR_CLIENT] [ERROR] Fallo enviando texto a {numero_destino}: {result}")
    return None


async def enviar_mensaje_qr_async(
    numero_destino: str,
    texto: str,
    reply_to_wamid: str = None,
    line_id: str = "qr_ventas_1",
) -> str | None:
    """Versión async de enviar_mensaje_qr (usa el sync en executor para no bloquear)."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: enviar_mensaje_qr(numero_destino, texto, reply_to_wamid, line_id),
    )


# ────────────────────────────────────────────────────────────
# Envío de multimedia
# ────────────────────────────────────────────────────────────

def enviar_media_qr(
    numero_destino: str,
    tipo_media: str,
    url_o_bytes: str | bytes,
    reply_to_wamid: str = None,
    caption: str = None,
    line_id: str = "qr_ventas_1",
) -> str | None:
    """
    Envía media (image, video, audio, document, sticker) vía Baileys.
    url_o_bytes: una URL pública o base64 str.
    Retorna el msg_id si tuvo éxito.
    """
    # Resolver URLs relativas locales (ej. stickers de la DB) a la ruta HTTP local de FastAPI
    parsed_url = url_o_bytes
    if isinstance(parsed_url, str) and not parsed_url.startswith("http"):
        if tipo_media == "sticker":
            parsed_url = f"http://127.0.0.1:8000/api/media/sticker/{parsed_url}"
        else:
            # Fallback for other local files if added in the future
            parsed_url = f"http://127.0.0.1:8000/api/media/{parsed_url}"

    payload = {
        "to": numero_destino,
        "type": tipo_media,
        "url": parsed_url if isinstance(parsed_url, str) else None,
    }
    if caption:
        payload["caption"] = caption

    result = _post("/api/qr/send-media", payload)
    if result and result.get("status") == "ok":
        msg_id = result.get("id")
        print(f"[QR_CLIENT] [OK] Media ({tipo_media}) enviada a {numero_destino}")
        import uuid
        return msg_id if msg_id else f"qr_media_sent_{uuid.uuid4().hex[:8]}"
    print(f"[QR_CLIENT] [ERROR] Fallo enviando media ({tipo_media}) a {numero_destino}: {result}")
    return None


# ────────────────────────────────────────────────────────────
# Descarga de multimedia recibida
# ────────────────────────────────────────────────────────────

def obtener_media_qr(media_id: str) -> tuple[bytes | None, str | None]:
    """
    Descarga los bytes de una media recibida por Baileys.
    media_id: empieza con "qr_" (ej: "qr_abc123xyz").
    Retorna (bytes, mime_type).
    """
    return _get_bytes(f"/api/qr/media/{media_id}")


# ────────────────────────────────────────────────────────────
# Reacciones
# ────────────────────────────────────────────────────────────

async def enviar_reaccion_qr(
    numero_destino: str,
    message_id: str,
    emoji: str,
    line_id: str = "qr_ventas_1",
) -> bool:
    """Envía una reacción emoji a un mensaje específico vía Baileys."""
    result = _post("/api/qr/react", {
        "to": numero_destino,
        "msgId": message_id,
        "emoji": emoji,
    })
    if result and result.get("status") == "ok":
        print(f"[QR_CLIENT] [OK] Reacción '{emoji}' enviada a {numero_destino}")
        return True
    print(f"[QR_CLIENT] [ERROR] Fallo enviando reacción a {numero_destino}: {result}")
    return False


# ────────────────────────────────────────────────────────────
# Resolución de LID → número de teléfono real
# ────────────────────────────────────────────────────────────

def resolver_lid_a_telefono(lid: str, line_id: str = "qr_ventas_1") -> str | None:
    """
    Consulta al microservicio Node.js para convertir un LID de 15 dígitos
    al número de teléfono real del cliente.
    Retorna el número limpio (ej: "51991616443") o None si no se puede resolver.
    """
    result = _get(f"/api/qr/resolve-lid/{lid}")
    if result and result.get("phone"):
        phone = result["phone"]
        print(f"[QR_CLIENT] [OK] LID {lid} resuelto -> {phone}")
        return phone
    print(f"[QR_CLIENT] [WARN] No se pudo resolver LID {lid}")
    return None

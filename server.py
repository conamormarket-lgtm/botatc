# ============================================================
#  server.py — Servidor FastAPI: webhook de WhatsApp + panel admin
#
#  FLUJO POR MENSAJE:
#  1. Meta envía POST /webhook con el mensaje del cliente
#  2. Extraemos número y texto del cliente
#  3. Normalizamos número → buscamos en Firebase
#  4. Si pedido en Diseño o no existe → silencio
#  5. Si bot activo → normalizar texto → llamar Groq → responder
#  6. Si [ESCALAR] detectado → pausar bot → marcar para humano
#  PANEL ADMIN: GET /admin → lista de chats escalados + botón reactivar
# ============================================================
import re
import json
import hashlib
from datetime import datetime, timedelta
import asyncio

from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE,
    META_VERIFY_TOKEN, SESION_EXPIRA_HORAS, ESTADOS_DISEÑO,
    MAX_HISTORIAL_TURNOS, ADMIN_PASSWORD
)
from prompts import get_system_prompt, MENSAJE_BIENVENIDA
from firebase_client import buscar_pedido_por_telefono
from whatsapp_client import enviar_mensaje, enviar_media
from bot_atc import normalizar_texto, preprocesar_mensaje

# ─────────────────────────────────────────────
#  Inicialización
# ─────────────────────────────────────────────
app = FastAPI(title="Bot ATC — IA-ATC")

def inyectar_tema_global(request, html: str) -> str:
    from server import obtener_usuario_sesion # ensure available
    usuario_sesion = obtener_usuario_sesion(request)
    prefs = usuario_sesion.get("preferencias_ui", {}) if usuario_sesion else {}
    c_bg = prefs.get('bg_main', '#0f172a')
    c_prim = prefs.get('primary_color', '#717f7f')
    c_acc = prefs.get('accent_bg', '#1e293b')
    wp = prefs.get('wallpaper', '')
    wp_opacity = float(prefs.get('wallpaper_opacity', '0.15'))
    wp_offset_y = prefs.get('wallpaper_offset_y', '50')
    wp_offset_x = prefs.get('wallpaper_offset_x', '50')
    t_main = prefs.get('text_main', '#f8fafc')
    t_muted = prefs.get('text_muted', '#94a3b8')

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
            --text-main: {t_main} !important;
            --text-muted: {t_muted} !important;
        }}
        .nav-item.active {{
            color: {t_main} !important;
            background-color: {accent_bg_rgba} !important;
            border-left: 3px solid {c_prim} !important;
        }}
    '''
    
    if wp:
        c_bg_hex = c_bg.lstrip('#')
        if len(c_bg_hex) == 6:
            c_bg_rgb = tuple(int(c_bg_hex[i:i+2], 16) for i in (0, 2, 4))
            overlay_alpha = 1.0 - wp_opacity
            overlay_rgba = f"rgba({c_bg_rgb[0]}, {c_bg_rgb[1]}, {c_bg_rgb[2]}, {overlay_alpha})"
        else:
            overlay_rgba = f"rgba(15, 23, 42, {1.0 - wp_opacity})"
            
        wp_lower = wp.lower()
        if wp_lower.endswith(".mp4") or wp_lower.endswith(".webm"):
            # En inyectar video usando background-color semi-transparente
            css += f'''
            .chat-viewer-panel {{
                position: relative;
                background-color: transparent !important;
                z-index: 1;
            }}
            .chat-list-panel {{
                background-color: {overlay_rgba} !important; /* Sidebar list keeps background */
            }}
            '''
            video_tag = f'''
            <video autoplay loop muted playsinline style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position: {wp_offset_x}% {wp_offset_y}%; z-index:-2; pointer-events:none;"><source src="{wp}"></video>
            <div style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:-1; pointer-events:none; background-color:{overlay_rgba};"></div>
            '''
            # Inyectamos el video dentro del panel visor de chat para no superponer listas u otros paneles
            if '<div class="chat-viewer-panel">' in html:
                html = html.replace('<div class="chat-viewer-panel">', f'<div class="chat-viewer-panel">\n{video_tag}')
            elif '<body' in html:
                import re
                html = re.sub(r'(<body[^>]*>)', rf'\1\n{video_tag}', html, count=1)
        else:
            css += f'''
            .chat-viewer-panel {{
                background: linear-gradient({overlay_rgba}, {overlay_rgba}), url('{wp}') !important;
                background-size: cover !important;
                background-position: {wp_offset_x}% {wp_offset_y}% !important;
            }}
            '''
            
        css += f'''
        .appearance-card, .proactive-card, .pdf-card, .backup-card, .editor-card {{
            background: var(--accent-bg) !important;
            border: 1px solid var(--accent-border) !important;
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
    html = html.replace("{wallpaper_opacity}", str(wp_opacity))
    html = html.replace("{wallpaper_offset_y}", str(wp_offset_y))
    html = html.replace("{wallpaper_offset_x}", str(wp_offset_x))
    html = html.replace("{text_main}", t_main)
    html = html.replace("{text_muted}", t_muted)
    return html

import traceback
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    err_str = f"Unhandled exception: {exc}\n{traceback.format_exc()}"
    with open("crash_log.txt", "w", encoding="utf-8") as file:
        file.write("\n--- CRASH ---\n")
        file.write(f"URL: {request.url}\n")
        file.write(err_str)
    print(err_str)
    return JSONResponse(status_code=500, content={"message": "Internal Server Error", "details": str(exc)})


import os
from fastapi.staticfiles import StaticFiles

if not os.path.exists("static"):
    try:
        os.makedirs("static", exist_ok=True)
    except Exception:
        pass

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

@app.on_event("startup")
def startup_event():
    # ── Restaurar toda la memoria y stickers desde Firebase ──
    try:
        from firebase_client import cargar_todas_las_sesiones
        # Restaurar sesiones (Inbox)
        sesiones_restauradas = cargar_todas_las_sesiones()
        for wa_id, s in sesiones_restauradas.items():
            sesiones[wa_id] = s
        print(f"[OK] Se restauraron {len(sesiones_restauradas)} conversaciones en memoria desde Firebase.")
        
        # Stickers are now loaded on-demand via Serverless Endpoints.
        
        # Restaurar Etiquetas
        from firebase_client import cargar_etiquetas_bd, cargar_grupos_bd
        global global_labels, global_groups
        global_labels = cargar_etiquetas_bd()
        print(f"[OK] Se restauraron {len(global_labels)} etiquetas globales.")
        global_groups = cargar_grupos_bd()
        print(f"[OK] Se restauraron {len(global_groups)} grupos virtuales.")
    except Exception as e:
        print(f"[ERROR] Error al restaurar datos desde Firebase: {e}")

    try:
        from pedidos_observer import iniciar_observador_pedidos
        import threading
        t = threading.Thread(target=iniciar_observador_pedidos, daemon=True)
        t.start()
    except: pass

# Sesiones en memoria: {numero_wa: SesionDict}
# numero_wa tiene código de país: "51945257117"
sesiones: dict[str, dict] = {}
global_labels: list = []
global_groups: list = []

# Interruptor global — False = bot completamente apagado
BOT_GLOBAL_ACTIVO: bool = True

# Cola para debouncing (acumular múltiples mensajes rápidos del mismo usuario)
mensajes_pendientes: dict[str, list[str]] = {}
import asyncio
user_locks: dict[str, asyncio.Lock] = {}
mensajes_procesados_ids = {}

# Caché de archivos multimedia (Audios, Imágenes, etc.) para que Gemini y el UI los lean
media_cache: dict[str, tuple[bytes, str]] = {}

async def cachear_media(media_id: str):
    if not media_id or media_id in media_cache: return
    try:
        from whatsapp_client import obtener_media_url, descargar_media
        url = await obtener_media_url(media_id)
        if url:
            contenido, mime = await descargar_media(url)
            if contenido: media_cache[media_id] = (contenido, mime)
    except: pass


# Regex para detectar escalación desde el mensaje del cliente
REGEX_ESCALAR = re.compile(
    r"\b(hablar con|comunicarme|persona real|humano|agente|asesor|"
    r"encargado|gerente|queja formal|reclamo|denuncia|responsable|"
    r"me comunican|quiero que me atienda|hablen conmigo)\b",
    re.IGNORECASE
)


# ─────────────────────────────────────────────
#  Gestión de sesiones
# ─────────────────────────────────────────────

def get_session_key(numero_wa: str, line_id: str = "principal") -> str:
    """
    Devuelve la clave compuesta para el dict de sesiones.
    - Para la línea principal usamos solo el número (retrocompatible).
    - Para líneas QR (prefijo 'qr_') usamos '{line_id}_{numero_wa}'.
    - Los phone_number_id numéricos de Meta son la línea principal.
    """
    if not line_id or line_id == "principal":
        return numero_wa
    # IDs numéricos son el phone_number_id real de Meta → línea principal
    if line_id.isdigit():
        return numero_wa
    # Solo las líneas con prefijo no-numérico (ej: qr_ventas_1) usan clave compuesta
    return f"{line_id}_{numero_wa}"


def obtener_o_crear_sesion(numero_wa: str, line_id: str = "principal") -> dict:
    """
    Retorna la sesión existente si está dentro del tiempo válido,
    la recupera de Firestore si el bot se reinició, o crea una nueva.
    Usa clave compuesta line_id+numero para separar conversaciones por línea.
    """
    ahora = datetime.utcnow()
    session_key = get_session_key(numero_wa, line_id)
    sesion = sesiones.get(session_key)

    if not sesion:
        # 1. Intentar cargar desde Firebase si el servidor se reinició
        try:
            from firebase_client import cargar_sesion_chat
            sesion_db = cargar_sesion_chat(session_key)
            if sesion_db:
                sesiones[session_key] = sesion_db
                sesion = sesion_db
                print(f"  [☁️ Historial recuperado desde la nube para {session_key}]")
        except Exception as e:
            print(f"  [[ERROR] Error al cargar historial de Firestore: {e}]")

    if sesion:
        pass # La sesión ya no expira nunca, como en un Inbox real

    if not sesion:
        sesiones[session_key] = {
            "historial":         [{"role": "system", "content": get_system_prompt()}],
            "datos_pedido":      None,
            "bot_activo":        True,
            "ultima_actividad":  ahora,
            "escalado_en":       None,
            "motivo_escalacion": None,
            "nombre_cliente":    "Cliente",
            "lineId":            line_id,
            "numero_real":       numero_wa,  # El número real del cliente, sin prefijo de línea
        }

    return sesiones[session_key]


def normalizar_numero(numero_wa: str) -> str:
    """
    Quita el código de país peruano para buscar en Firebase.
    '51945257117' → '945257117'
    """
    digitos = numero_wa.replace("+", "").strip()
    if digitos.startswith("51") and len(digitos) == 11:
        return digitos[2:]
    return digitos


# ─────────────────────────────────────────────
#  Llamada al modelo (Gemini)
# ─────────────────────────────────────────────

def llamar_gemini(historial: list[dict]) -> str:
    """Llama a Gemini con el historial y retorna la respuesta del modelo."""
    try:
        # El primer mensaje siempre es el sistema
        system_text = historial[0]["content"]
        
        # Mapeamos el historial a formato Gemini, uniendo roles consecutivos si los hay
        gemini_contents = []
        for msg in historial[1:]:
            role = "model" if msg["role"] == "assistant" else "user"
            
            # CRÍTICO: Gemini exige que la conversación inicie obligatoriamente con el usuario.
            if not gemini_contents and role == "model":
                continue
            
            # Buscar si el mensaje es un audio (enviado por el cliente)
            match_audio = re.match(r"^\[audio:([^\]]+)\]$", msg["content"].strip())
            
            part = None
            if match_audio:
                media_id = match_audio.group(1)
                audio_data = media_cache.get(media_id)
                if audio_data:
                    contenido_bytes, mime_type = audio_data
                    # Depurar codecs en mime_type (ej. audio/ogg; codecs=opus -> audio/ogg)
                    if mime_type and ";" in mime_type: mime_type = mime_type.split(";")[0]
                    if not mime_type: mime_type = "audio/ogg" 
                    part = types.Part.from_bytes(data=contenido_bytes, mime_type=mime_type)
                else:
                    part = types.Part.from_text(text="[🎤 Mensaje de voz (Audio expirado o no disponible en caché)]")
            else:
                part = types.Part.from_text(text=msg["content"])
                
            if gemini_contents and gemini_contents[-1].role == role:
                gemini_contents[-1].parts.append(part)
            else:
                gemini_contents.append(types.Content(role=role, parts=[part]))
                
        # Doble verificación final: si por alguna razón no quedó nada
        if not gemini_contents:
            gemini_contents.append(types.Content(role="user", parts=[types.Part.from_text(text="[Retomando la conversación]")]))
            
        config = types.GenerateContentConfig(
            system_instruction=system_text,
            temperature=TEMPERATURE,
            max_output_tokens=2048,
            safety_settings=[
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            ]
        )
        import time
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=gemini_contents,
                    config=config,
                )
                return response.text.strip()
            except Exception as e:
                err_str = str(e)
                # Retry on rate limits or temporary unavailability
                if "503" in err_str or "unloaded" in err_str or "UNAVAILABLE" in err_str or "429" in err_str or "ResourceExhausted" in err_str or "quota" in err_str.lower():
                    if attempt < max_retries - 1:
                        wait_t = 2 ** attempt  # 1s, 2s, 4s
                        print(f"  [[WARN] Gemini saturado: {err_str} | Reintentando en {wait_t}s (Intento {attempt+1}/{max_retries})]")
                        time.sleep(wait_t)
                        continue
                
                # If it's not a retriable error or we exhausted retries
                import traceback
                with open("error_gemini.txt", "w") as f:
                    f.write(traceback.format_exc())
                print(f"[ERROR] Error Gemini definitivo: {e}")
                return ""
        return ""
    except Exception as general_e:
        import traceback
        with open("error_gemini.txt", "w") as f:
            f.write(traceback.format_exc())
        print(f"[ERROR] Error crítico en llamar_gemini (fuera del reintento): {general_e}")
        return ""

def recortar_historial(historial: list[dict]) -> list[dict]:
    """Conserva system prompt + últimos N turnos, asegurando que inicie con 'user'."""
    system = [historial[0]]
    turnos = historial[1:]
    
    # Si excede el límite (ej. 6 = 3 turnos usuario-asistente)
    if len(turnos) > MAX_HISTORIAL_TURNOS * 2:
        turnos = turnos[-(MAX_HISTORIAL_TURNOS * 2):]
        
        # Gemini (y Groq) requieren que el primer mensaje después del system sea del 'user'.
        # Si al cortar el array el primer elemento quedó como 'assistant' (model), lo volamos para emparejar.
        if turnos and turnos[0]["role"] == "assistant":
            turnos = turnos[1:]
            
    return system + turnos


# ─────────────────────────────────────────────
#  Lógica de escalación
# ─────────────────────────────────────────────

def procesar_escalacion(numero_wa: str, sesion: dict, respuesta_bot: str) -> str:
    """
    Detecta [ESCALAR] en la respuesta del bot y actualiza la sesión.
    Retorna la respuesta limpia (sin la etiqueta).
    """
    if "[ESCALAR]" in respuesta_bot:
        respuesta_limpia = respuesta_bot.replace("[ESCALAR]", "").strip()
        sesion["bot_activo"] = False
        sesion["escalado_en"] = datetime.utcnow()
        sesion["motivo_escalacion"] = "Detectado por el modelo"
        print(f"  [🚨 ESCALADO → {numero_wa} | {sesion['nombre_cliente']}]")
        return respuesta_limpia
    return respuesta_bot


# ─────────────────────────────────────────────
#  Webhook de Meta
# ─────────────────────────────────────────────

@app.get("/webhook")
async def verificar_webhook(request: Request):
    """
    Meta hace un GET para verificar que el servidor es legítimo.
    Responde con hub.challenge si el token coincide.
    """
    params = dict(request.query_params)
    mode      = params.get("hub.mode")
    token     = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == META_VERIFY_TOKEN:
        print("[OK] Webhook de Meta verificado correctamente.")
        return int(challenge)

    raise HTTPException(status_code=403, detail="Token de verificación incorrecto.")


@app.post("/webhook")
async def recibir_mensaje(request: Request, background_tasks: BackgroundTasks):
    """
    Recibe mensajes entrantes de Meta y procesa la conversación.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # Meta envía varios tipos de eventos; solo nos interesan mensajes de texto
    try:
        entry    = body["entry"][0]
        changes  = entry["changes"][0]["value"]

        # Manejar estados de entrega (palomitas)
        if "statuses" in changes:
            for st in changes["statuses"]:
                msg_wamid = st.get("id")
                status_val = st.get("status")
                num_wa = st.get("recipient_id")
                if num_wa and num_wa in sesiones:
                    se = sesiones[num_wa]
                    for it in reversed(se.get("historial", [])):
                        if it.get("msg_id") == msg_wamid:
                            # Evitar degradar el estado (ej. de read a delivered)
                            jerarquia = {"sent": 1, "delivered": 2, "read": 3}
                            old_st = it.get("status", "sent")
                            if jerarquia.get(status_val, 0) >= jerarquia.get(old_st, 0):
                                it["status"] = status_val
                                import time
                                ts_now = int(time.time())
                                if status_val == "delivered" and not it.get("delivered_ts"):
                                    it["delivered_ts"] = ts_now
                                elif status_val == "read" and not it.get("read_ts"):
                                    it["read_ts"] = ts_now
                                try:
                                    from firebase_client import guardar_sesion_chat
                                    guardar_sesion_chat(num_wa, se)
                                except: pass
                            break
            return {"status": "ok"}

        # Si no hay mensajes, ignorar
        if "messages" not in changes:
            return {"status": "ok"}

        mensaje_data  = changes["messages"][0]
        mensaje_id    = mensaje_data.get("id", "")
        mensaje_ts    = mensaje_data.get("timestamp", "")
        
        # Ignorar mensajes duplicados enviados repetidamente por el webhook de Meta (sesión actual)
        if mensaje_id in mensajes_procesados_ids:
            return {"status": "ok"}
        mensajes_procesados_ids[mensaje_id] = True
        
        # Mantener solo los últimos 1000 IDs para evitar fugas sin vaciar el historial reciente
        if len(mensajes_procesados_ids) > 1000:
            oldest = next(iter(mensajes_procesados_ids))
            del mensajes_procesados_ids[oldest]
            
        numero_wa     = mensaje_data["from"]           # ej: "51945257117" — Meta siempre envía con código de país
        tipo_mensaje  = mensaje_data.get("type", "")

        # Ignorar si el webhook trata de entregar un mensaje que YA fue guardado históricamente
        # (clave compuesta para aislamiento multisucursal)
        session_key_check = get_session_key(numero_wa, changes.get("metadata", {}).get("phone_number_id", "principal"))
        if session_key_check in sesiones:
            for it_hist in reversed(sesiones[session_key_check].get("historial", [])):
                if it_hist.get("msg_id") == mensaje_id:
                    return {"status": "ok"}

        # Obtener nombre de contacto
        nombre = "Cliente"
        if "contacts" in changes and changes["contacts"]:
            nombre = changes["contacts"][0].get("profile", {}).get("name", "Cliente")

        # Procesar según tipo de mensaje
        if tipo_mensaje == "text":
            texto_cliente = mensaje_data["text"]["body"].strip()
        elif tipo_mensaje == "sticker":
            media_id = mensaje_data.get("sticker", {}).get("id", "")
            texto_cliente = f"[sticker:{media_id}]"
            background_tasks.add_task(cachear_media, media_id)
        elif tipo_mensaje == "image":
            img_data = mensaje_data.get("image", {})
            is_view_once = img_data.get("view_once", False)
            media_id = img_data.get("id", "")
            caption  = img_data.get("caption", "")
            if is_view_once:
                texto_cliente = f"[vista_unica:imagen]" + (f" {caption}" if caption else "")
                from whatsapp_client import enviar_mensaje_texto
                background_tasks.add_task(enviar_mensaje_texto, numero_wa, "Lo sentimos, por motivos del sistema no podemos visualizar archivos enviados como *Vista Única*. 🚫👁️\n\nPor favor, *vuelve a enviarlo desactivando el icono (1)* para que podamos verlo y atenderte.")
            else:
                texto_cliente = f"[imagen:{media_id}]" + (f" {caption}" if caption else "")
                background_tasks.add_task(cachear_media, media_id)
        elif tipo_mensaje in ["audio", "voice"]:
            # WhatsApp puede enviar audio (grabados) o voice (voice notes)
            aud_data = mensaje_data.get(tipo_mensaje, {})
            is_view_once = aud_data.get("view_once", False)
            media_id = aud_data.get("id", "")
            if is_view_once:
                texto_cliente = f"[vista_unica:audio]"
                from whatsapp_client import enviar_mensaje_texto
                background_tasks.add_task(enviar_mensaje_texto, numero_wa, "Lo sentimos, por motivos del sistema no podemos escuchar audios marcados como *Vista Única*. 🚫👁️\n\nPor favor, *vuelve a enviarlo de forma normal* para que podamos escucharlo.")
            else:
                texto_cliente = f"[audio:{media_id}]"
                background_tasks.add_task(cachear_media, media_id)
        elif tipo_mensaje == "video":
            vid_data = mensaje_data.get("video", {})
            is_view_once = vid_data.get("view_once", False)
            if is_view_once:
                texto_cliente = "[vista_unica:video]"
                from whatsapp_client import enviar_mensaje_texto
                background_tasks.add_task(enviar_mensaje_texto, numero_wa, "Lo sentimos, por motivos del sistema no podemos visualizar videos enviados como *Vista Única*. 🚫👁️\n\nPor favor, *vuelve a enviarlo desactivando el icono (1)* para que podamos verlo.")
            else:
                media_id = vid_data.get("id", "")
                caption = vid_data.get("caption", "")
                texto_cliente = f"[video:{media_id}]"
                if caption:
                    import urllib.parse
                    caption_encoded = urllib.parse.quote(caption)
                    texto_cliente = f"[video:{media_id}|caption:{caption_encoded}]"
                background_tasks.add_task(cachear_media, media_id)
        elif tipo_mensaje == "document":
            filename = mensaje_data.get("document", {}).get("filename", "archivo")
            media_id = mensaje_data.get("document", {}).get("id", "")
            texto_cliente = f"[documento:{media_id}|{filename}]"
        elif tipo_mensaje == "reaction":
            reaction_data = mensaje_data.get("reaction", {})
            emoji = reaction_data.get("emoji", "")
            msg_id_reacted = reaction_data.get("message_id", "")
            
            texto_original = "un mensaje"
            if numero_wa in sesiones:
                for m_hist in sesiones[numero_wa]["historial"]:
                    if m_hist.get("msg_id") == msg_id_reacted:
                        txt = m_hist.get("content", "")
                        if txt.startswith("["): 
                            txt = txt.split("]")[0] + "]"
                        texto_original = (txt[:40] + '...') if len(txt) > 40 else txt
                        break
            
            if emoji:
                texto_cliente = f"[💬 Reacción: {emoji} a «{texto_original}»]"
            else:
                texto_cliente = f"[[ERROR] Quitó reacción a «{texto_original}»]"
        elif tipo_mensaje == "location":
            lat = mensaje_data.get("location", {}).get("latitude", "")
            lon = mensaje_data.get("location", {}).get("longitude", "")
            addr = mensaje_data.get("location", {}).get("address", "")
            texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
        elif tipo_mensaje == "button":
            texto_cliente = "🎯 " + mensaje_data.get("button", {}).get("text", "Botón")
        elif tipo_mensaje == "interactive":
            inter = mensaje_data.get("interactive", {})
            tipo_inter = inter.get("type", "")
            if tipo_inter == "button_reply":
                texto_cliente = "🎯 " + inter.get("button_reply", {}).get("title", "Botón")
            elif tipo_inter == "list_reply":
                texto_cliente = "📋 " + inter.get("list_reply", {}).get("title", "Opción")
            else:
                texto_cliente = "[Interacción]"
        else:
            texto_cliente = f"[{tipo_mensaje}]"

    except (KeyError, IndexError):
        return {"status": "ok"}   # payload inesperado → ignorar sin error

    # Detectar si el cliente está usando la función de deslizar/responder
    contexto = changes["messages"][0].get("context", {})
    if "id" in contexto:
        reply_id = contexto["id"]
        texto_citado = "uno de tus mensajes"
        
        # Buscar en RAM el mensaje original para mostrarlo
        if numero_wa in sesiones:
            for msg_item in reversed(sesiones[numero_wa].get("historial", [])):
                if msg_item.get("msg_id") == reply_id:
                    texto_crudo = msg_item.get("content", "")
                    texto_limpio = texto_crudo.replace("\n", " ").strip()
                    if texto_limpio:
                        texto_citado = texto_limpio[:40] + ("..." if len(texto_limpio) > 40 else "")
                    break
                    
        texto_cliente = f"[[REPLY|{texto_citado}]]{texto_cliente}"

    print(f"\n{'─'*50}")
    print(f"📨 {nombre} ({numero_wa}): {texto_cliente}")

    # Extraer la línea destino para segmentación multisucursal
    phone_number_id = changes.get("metadata", {}).get("phone_number_id", "principal")

    # --- AGREGAR AL HISTORIAL INMEDIATAMENTE PARA QUE EL UI LO VEA EN BURBUJAS SEPARADAS ---
    session_key = get_session_key(numero_wa, phone_number_id)
    ses = obtener_o_crear_sesion(numero_wa, phone_number_id)
    ses["ultima_actividad"] = datetime.utcnow()
    ses["nombre_cliente"]   = nombre
    ses["lineId"]           = phone_number_id
    ses["numero_real"]      = numero_wa
    if not ses["historial"] or ses["historial"][-1].get("msg_id") != mensaje_id:
        import time
        ses["historial"].append({"role": "user", "content": texto_cliente, "msg_id": mensaje_id, "timestamp": int(time.time())})
        cur_unread = ses.get("unread_count", 0)
        ses["unread_count"] = 1 if cur_unread == -1 else cur_unread + 1
        try: 
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(session_key, ses)
        except: 
            pass
    # -----------------------------------------------------------------------------------------

    dict_msg = {"texto": texto_cliente, "id": mensaje_id}
    if session_key not in mensajes_pendientes:
        mensajes_pendientes[session_key] = [dict_msg]
        background_tasks.add_task(procesador_agregado, session_key, nombre)
    else:
        mensajes_pendientes[session_key].append(dict_msg)

    return {"status": "ok"}


# ─────────────────────────────────────────────
#  Webhook del microservicio QR (Baileys)
# ─────────────────────────────────────────────
@app.post("/webhook_qr")
async def recibir_mensaje_qr(request: Request, background_tasks: BackgroundTasks):
    """Endpoint desactivado — procesamiento de mensajes QR pausado hasta migración a nueva librería."""
    return {"status": "ok"}

@app.get("/api/settings/qr_status")
def get_qr_status():
    """Proxy local para consultar el estado del microservicio Baileys Node.js"""
    try:
        import urllib.request
        import json
        req = urllib.request.Request("http://localhost:3000/api/qr/link", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        err_msg = f"Exception: {type(e).__name__} - {str(e)}"
        print("ERROR IN GET_QR_STATUS:", err_msg)
        return {"status": "error", "message": f"Falla urllib: {err_msg}"}

async def procesador_agregado(numero_wa: str, nombre: str):
    """
    Espera 3.0 segundos de 'silencio' para ver si el cliente manda otro mensaje rápido.
    Si llegan más, se agregan a la cola en el endpoint y luego se procesan juntos.
    """
    import asyncio
    import anyio
    
    await asyncio.sleep(3.0)  # Ventana de agregación de 3.0s
    
    # Obtener el lock del usuario para evitar llamadas superpuestas al modelo
    if numero_wa not in user_locks:
        user_locks[numero_wa] = asyncio.Lock()
        
    lock = user_locks[numero_wa]
    
    async with lock:
        # Extraemos los mensajes RECIÉN AHORA
        textos_dicts = mensajes_pendientes.pop(numero_wa, [])
        if not textos_dicts:
            return
            
        # Compatibilidad con variables en memoria del formato viejo
        if isinstance(textos_dicts[0], str):
            texto_unido = " | ".join(textos_dicts)
            last_id = None
        else:
            texto_unido = " | ".join([m["texto"] for m in textos_dicts])
            last_id = textos_dicts[-1]["id"]
        
        # Ejecutar el proceso pesado sincrónico en un hilo separado
        await anyio.to_thread.run_sync(
            procesar_mensaje_interno, numero_wa, nombre, texto_unido, False, last_id
        )


def procesar_mensaje_interno(numero_wa: str, nombre: str, texto_cliente: str, is_simulacion: bool = False, msg_id: str = None) -> str | None:
    """Procesa un mensaje y devuelve la respuesta del bot (si la hay) sin enviarla si es simulación."""

    # ── Obtener/crear sesión ──────────────────────────────
    sesion = obtener_o_crear_sesion(numero_wa)
    sesion["ultima_actividad"] = datetime.utcnow()
    sesion["nombre_cliente"]   = nombre

    # 1) Para simulaciones, guardamos el mensaje aquí. Para en vivo, recibir_mensaje ya lo guarda al instante.
    if is_simulacion:
        if not sesion["historial"] or sesion["historial"][-1].get("msg_id") != msg_id:
            import time
            ts = int(time.time()) # fallback
            sesion["historial"].append({"role": "user", "content": texto_cliente, "msg_id": msg_id, "timestamp": ts})
            
            try: 
                from firebase_client import guardar_sesion_chat
                guardar_sesion_chat(numero_wa, sesion)
            except Exception as e:
                pass

    from bot_manager import get_bot_for_line, is_bot_active
    line_id = sesion.get("lineId", "principal")
    bot_id = get_bot_for_line(line_id)

    if not bot_id or not is_bot_active(bot_id):
        print(f"  [⏹ Bot no asignado o inactivo para la línea '{line_id}' → silencio (humano atiende)]")
        return None

    # ── Si el bot está pausado (modo humano) → guardar el msg y silenciar ───
    if not sesion.get("bot_activo", True):
        sesion["ultima_actividad"] = datetime.utcnow()
        print(f"  [👤 Bot pausado → mensaje guardado en historial, humano atiende]")
        try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
        except: pass
        return None

    # ── Buscar pedido en Firebase (con número del WA) ─────
    if sesion["datos_pedido"] is None:
        from config import NUMEROS_TESTER
        numero_local = normalizar_numero(numero_wa)
        es_tester = numero_local in NUMEROS_TESTER or numero_wa in NUMEROS_TESTER
        
        # Guardamos el mensaje temprano para que SIEMPRE aparezca en el Inbox admin
        texto_historial = texto_cliente
        partes_media = []
        if isinstance(texto_cliente, str):
            if "[sticker:" in texto_cliente or "[imagen:" in texto_cliente:
                pass # Already structured
                


        # ── MODO TESTER: preguntar N° de pedido manualmente ──
        if es_tester:
            # Si ya nos dijo el número de pedido, buscarlo por ID
            if sesion.get("esperando_pedido_tester"):
                from firebase_client import inicializar_firebase
                db = inicializar_firebase()
                id_pedido = texto_cliente.strip().upper()
                try:
                    doc = db.collection("pedidos").document(id_pedido).get()
                    datos = doc.to_dict() if doc.exists else None
                except Exception:
                    datos = None

                if datos:
                    sesion["esperando_pedido_tester"] = False
                    sesion["datos_pedido"] = datos
                    sesion["nombre_cliente"] = f"{datos.get('clienteNombre','')} {datos.get('clienteApellidos','')}".strip() or nombre
                    sesion["historial"][0] = {"role": "system", "content": get_system_prompt(datos, bot_id)}
                    print(f"  [🧪 TESTER: Pedido '{id_pedido}' cargado]")
                else:
                    msg = f"[ERROR] No encontré ningún pedido con el ID '{texto_cliente.strip()}'. Inténtalo de nuevo (escribe solo el ID exacto)."
                    import time
                    ts = int(time.time())
                    sesion["historial"].append({"role": "assistant", "content": msg, "status": "sent", "timestamp": ts})
                    try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
                    except: pass
                    if not is_simulacion:
                        enviar_mensaje(numero_wa, msg)
                    return msg
            else:
                # Primera vez: pedir el ID de pedido
                sesion["esperando_pedido_tester"] = True
                msg = "🧪 *Modo prueba activado.*\n\nEscríbeme el ID del pedido que deseas probar (tal como aparece en Firebase):"
                import time
                ts = int(time.time())
                sesion["historial"].append({"role": "assistant", "content": msg, "status": "sent", "timestamp": ts})
                if not is_simulacion:
                    enviar_mensaje(numero_wa, msg)
                return msg
        else:
            datos_lista = buscar_pedido_por_telefono(numero_local)
            if datos_lista:
                # Excluir pedidos que están en Diseño
                pedidos_no_diseno = [d for d in datos_lista if d.get("estadoGeneral", "") not in ESTADOS_DISEÑO]
                
                if not pedidos_no_diseno:
                    print(f"  [🎨 Todos en Diseño → silencio]")
                    return None
                    
                nombre_cliente = f"{pedidos_no_diseno[0].get('clienteNombre','')} {pedidos_no_diseno[0].get('clienteApellidos','')}".strip()
                sesion["nombre_cliente"] = nombre_cliente or nombre
                
                ids = [p.get("id") for p in pedidos_no_diseno]
                print(f"  [[OK] Pedidos encontrados: {ids} | Evitando Diseño]")
                
                sesion["datos_pedido"] = pedidos_no_diseno[0]  # Backward compatibility for inbox
                sesion["pedidos_multiples"] = pedidos_no_diseno
                
                sesion["historial"][0] = {
                    "role": "system",
                    "content": get_system_prompt(pedidos_no_diseno, bot_id)
                }
            else:
                print(f"  [❓ Sin pedido registrado → silencio]")
                try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
                except: pass
                return None
    else:
        # Refrescar los datos para evitar estado obsoleto
        from config import NUMEROS_TESTER
        numero_local = normalizar_numero(numero_wa)
        es_tester = numero_local in NUMEROS_TESTER or numero_wa in NUMEROS_TESTER
        
        if not es_tester:
            datos_lista_fresca = buscar_pedido_por_telefono(numero_local)
            if datos_lista_fresca:
                pedidos_no_diseno = [d for d in datos_lista_fresca if d.get("estadoGeneral", "") not in ESTADOS_DISEÑO]
                if pedidos_no_diseno:
                    sesion["datos_pedido"] = pedidos_no_diseno[0]
                    sesion["pedidos_multiples"] = pedidos_no_diseno
                    if sesion["historial"] and sesion["historial"][0]["role"] == "system":
                        sesion["historial"][0]["content"] = get_system_prompt(pedidos_no_diseno, bot_id)
        else:
            # Re-fetch the specific manual ID for the tester
            id_tester = sesion["datos_pedido"].get("id")
            if id_tester:
                from firebase_client import inicializar_firebase
                db = inicializar_firebase()
                try:
                    doc = db.collection("pedidos").document(id_tester).get()
                    if doc.exists:
                        datos_tester = doc.to_dict()
                        sesion["datos_pedido"] = datos_tester
                        if sesion["historial"] and sesion["historial"][0]["role"] == "system":
                            # Mantener formato de lista si usa el nuevo modelo multipedido
                            sesion["historial"][0]["content"] = get_system_prompt([datos_tester] if "pedidos_multiples" in sesion else datos_tester, bot_id)
                except:
                    pass

        estado_actual = sesion["datos_pedido"].get("estadoGeneral", "")
        if estado_actual in ESTADOS_DISEÑO:
            print(f"  [🎨 Pedido volvió a Diseño → silencio]")
            try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
            except: pass
            return None



    # ── Escalación rápida por keywords del cliente ────────
    if REGEX_ESCALAR.search(texto_cliente):
        print(f"  [🚨 Escalación por keyword detectada]")
        sesion["bot_activo"]        = False
        sesion["escalado_en"]       = datetime.utcnow()
        sesion["motivo_escalacion"] = f"Keyword: '{texto_cliente[:60]}'"
        msg = "Voy a avisarle a uno de nuestros asesores para que te escriba por aquí en breve. 😊"
        if not is_simulacion:
            enviar_mensaje(numero_wa, msg)
            
        try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
        except: pass
        
        return msg

    # ── Preprocesar texto (normalizar + cancelar=pagar) ───
    texto_modelo = preprocesar_mensaje(normalizar_texto(texto_cliente))

    # ── Agregar al historial y llamar al modelo ───────────
    # Creamos la copia para Gemini SIN alterar el historial persistente para que en el UI sigan las burbujas separadas.
    historial_para_gemini = recortar_historial(sesion["historial"])
    if historial_para_gemini and historial_para_gemini[-1]["role"] == "user":
        # Usamos texto_modelo que concatena todo con ' | ' para que la IA entienda el contexto fusionado
        historial_para_gemini[-1]["content"] = texto_modelo
        
    print(f"  [🧠 Enviando {len(historial_para_gemini)} turnos a Gemini]")
    respuesta_bot = llamar_gemini(historial_para_gemini)
    
    if not respuesta_bot.strip():
        # Falla silenciosamente si Gemini no genera respuesta útil o tira error
        print("  [[ERROR] Respuesta vacía de Gemini. Ignorando...]")
        return None

    # ── Procesar escalación si el modelo la detectó ───────
    respuesta_final = procesar_escalacion(numero_wa, sesion, respuesta_bot)

    # ── Enviar respuesta al cliente por WhatsApp ──────────
    print(f"🤖 María: {respuesta_final[:80]}...")
    wamid_out = None
    if not is_simulacion:
        # Parsear si el bot incluyó etiquetas [sticker:...], [imagen:...]
        partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\])', respuesta_final)
        for p in partes:
            p = p.strip()
            if not p: continue
            
            match_sticker = re.match(r"^\[sticker:([^\]]+)\]$", p)
            match_img = re.match(r"^\[imagen:([^\]]+)\]$", p)
            
            if match_sticker: wamid_out = enviar_media(numero_wa, "sticker", match_sticker.group(1)) or wamid_out
            elif match_img: wamid_out = enviar_media(numero_wa, "image", match_img.group(1)) or wamid_out
            else: wamid_out = enviar_mensaje(numero_wa, p) or wamid_out

    # ── Guardar respuesta en historial ────────────────────
    import time
    ts = int(time.time())
    sesion["historial"].append({"role": "assistant", "content": respuesta_final, "msg_id": wamid_out, "status": "sent", "timestamp": ts, "sent_by": "IA Bot"})

    
    try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
    except: pass
    
    return respuesta_final


# ─────────────────────────────────────────────
#  Panel de administración
# ─────────────────────────────────────────────



from fastapi import Response

VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
import json, os

# ─── Sesiones de usuarios (auth) persitidas en Firebase ───────────────────────
# active_sessions: {token: user_dict}
active_sessions = {}

def _load_sessions_from_firebase():
    """Carga todas las sesiones activas desde Firestore al arrancar el servidor."""
    global active_sessions
    try:
        from firebase_client import inicializar_firebase
        db = inicializar_firebase()
        if not db: return
        docs = db.collection("auth_sessions").stream()
        for doc in docs:
            active_sessions[doc.id] = doc.to_dict()
        print(f"[OK] Se restauraron {len(active_sessions)} sesiones de usuario desde Firebase.")
    except Exception as e:
        print(f"[ERROR] Error cargando sesiones de usuario: {e}")

_load_sessions_from_firebase()

def save_sessions():
    """Persiste todas las sesiones activas en Firestore."""
    try:
        from firebase_client import inicializar_firebase
        db = inicializar_firebase()
        if not db: return
        col = db.collection("auth_sessions")
        # Guardar solo las sesiones actuales
        for token, user_data in active_sessions.items():
            col.document(token).set(user_data)
    except Exception as e:
        print(f"[ERROR] Error guardando sesiones de usuario: {e}")

def delete_session_from_firebase(token: str):
    """Elimina una sesión específica de Firestore al hacer logout."""
    try:
        from firebase_client import inicializar_firebase
        db = inicializar_firebase()
        if db: db.collection("auth_sessions").document(token).delete()
    except: pass


def obtener_usuario_sesion(request: Request) -> dict | None:
    token = request.cookies.get("session_token")
    if token and token in active_sessions:
        return active_sessions[token]
    return None

def verificar_sesion(request: Request):
    user = obtener_usuario_sesion(request)
    if user and user.get("estado") == "aprobado":
        return True
    return False

def es_admin(request: Request):
    user = obtener_usuario_sesion(request)
    return user and "admin" in user.get("permisos", []) and user.get("estado") == "aprobado"

@app.get("/login", response_class=HTMLResponse)

async def login_get():
    return obtener_login_html()


import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()



@app.post("/login")
async def login_post(response: Response, username: str = Form(None), password: str = Form(None), google_token: str = Form(None), action: str = Form("login"), remember: str = Form(None)):

    from firebase_client import obtener_usuario, crear_usuario
    
    user_data = None
    
    if google_token:
        try:
            from google.oauth2 import id_token
            import google.auth.transport.requests
            request_g = google.auth.transport.requests.Request()
            # Idealmente deberíamos validar el CLIENT_ID passandolo a audience=..., por ahora solo validamos firma
            val = id_token.verify_oauth2_token(google_token, request_g)
            email = val.get("email")
            parsed_username = email.split('@')[0]
            
            user_data = obtener_usuario(parsed_username)
            if not user_data:
                # auto-registrar si no existe
                crear_usuario(parsed_username, "GOOGLE_AUTH")
                return HTMLResponse(obtener_login_html(error="Cuenta vinculada con Google. Espera a que un administrador apruebe tu cuenta.", success=True), status_code=200)
                
            if user_data.get("estado") != "aprobado":
                return HTMLResponse(obtener_login_html(error="Tu cuenta de Google está pendiente de aprobación."), status_code=403)
                
        except Exception as e:
            return HTMLResponse(obtener_login_html(error=f"Error validando Google Token: {str(e)}"), status_code=401)
            
    else:
        if not username or not password:
            return HTMLResponse(obtener_login_html(error="Faltan credenciales."), status_code=400)
            
        if action == "register":
            exito = crear_usuario(username, hash_password(password))
            if exito:
                return HTMLResponse(obtener_login_html(error="Cuenta creada. Espera a que un administrador la apruebe.", success=True), status_code=200)
            else:
                return HTMLResponse(obtener_login_html(error="El usuario ya existe."), status_code=400)

        # Basic Login
        if username == "admin" and password == ADMIN_PASSWORD:
            user_data = {"username": "admin", "estado": "aprobado", "permisos": ["admin"]}
        else:
            user_data = obtener_usuario(username)
            if not user_data or user_data.get("password") != hash_password(password):
                return HTMLResponse(obtener_login_html(error="Usuario o clave incorrectos."), status_code=401)
            if user_data.get("estado") != "aprobado":
                return HTMLResponse(obtener_login_html(error="Tu cuenta está pendiente de aprobación."), status_code=403)

    import uuid
    token = str(uuid.uuid4())
    active_sessions[token] = user_data
    save_sessions()
    

    resp = RedirectResponse(url="/inbox", status_code=303)
    if remember == "yes" or google_token:
        resp.set_cookie(key="session_token", value=token, httponly=True, max_age=2592000) # 30 días
    else:
        resp.set_cookie(key="session_token", value=token, httponly=True) # cookie de sesión (se borra al cerrar el navegador)
    return resp



    if action == "register":
        from firebase_client import crear_usuario
        exito = crear_usuario(username, hash_password(password))
        if exito:
            return HTMLResponse(obtener_login_html(error="Cuenta creada. Espera a que un administrador la apruebe.", success=True), status_code=200)
        else:
            return HTMLResponse(obtener_login_html(error="El usuario ya existe."), status_code=400)

    # Es Login
    from firebase_client import obtener_usuario
    # Soporte para la cuenta admin inicial de rescate
    if username == "admin" and password == ADMIN_PASSWORD:
        user_data = {"username": "admin", "estado": "aprobado", "permisos": ["admin"]}
    else:
        user_data = obtener_usuario(username)
        if not user_data or user_data.get("password") != hash_password(password):
            return HTMLResponse(obtener_login_html(error="Usuario o clave incorrectos."), status_code=401)
        
        if user_data.get("estado") != "aprobado":
            return HTMLResponse(obtener_login_html(error="Tu cuenta está pendiente de aprobación por un administrador."), status_code=403)

    import uuid
    token = str(uuid.uuid4())
    active_sessions[token] = user_data
    save_sessions()
    
    # Redirigir al inbox por defecto

    resp = RedirectResponse(url="/inbox", status_code=303)
    if remember == "yes" or google_token:
        resp.set_cookie(key="session_token", value=token, httponly=True, max_age=2592000) # 30 días
    else:
        resp.set_cookie(key="session_token", value=token, httponly=True) # cookie de sesión (se borra al cerrar el navegador)
    return resp


@app.get("/logout")

async def logout(request: Request):
    token = request.cookies.get("session_token")
    if token in active_sessions:
        del active_sessions[token]
    delete_session_from_firebase(token)
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session_token")
    return resp


def obtener_login_html(error="", success=False):
    msg_html = f'<div class="error" style="color: {"#10b981" if success else "#ef4444"}; background: {"#064e3b" if success else "#451a1e"}; border: 1px solid {"#059669" if success else "#991b1b"}; padding: 10px; border-radius: 8px; margin-bottom: 20px; font-size: 0.9em; text-align: center;">{error}</div>' if error else ''
    return f"""
    <html><head><title>Acceso Restringido — IA-ATC</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;700&display=swap" rel="stylesheet">
    <style>
      :root {{
          --primary-color: #717f7f; --primary-hover: #2563eb;
          --bg-main: #0f172a; --bg-card: #1e293b; --text-color: #f8fafc;
      }}
      body {{
          background-color: var(--bg-main); color: var(--text-color);
          font-family: 'Inter', sans-serif; display: flex;
          align-items: center; justify-content: center; height: 100vh; margin: 0;
      }}
      .login-box {{
          background-color: var(--bg-card); padding: 40px;
          border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
          width: 100%; max-width: 350px;
      }}
      h2 {{ text-align: center; font-family: 'Outfit', sans-serif; font-size: 24px; margin-top: 0; margin-bottom: 30px; letter-spacing: -0.5px; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab-btn {{ flex: 1; padding: 10px; text-align: center; border: none; background: transparent; color: #94a3b8; font-family: 'Outfit', sans-serif; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.3s ease; }}
        .tab-btn.active {{ color: var(--primary-color); border-bottom-color: var(--primary-color); }}
      input {{
          width: 100%; padding: 12px; margin-bottom: 20px;
          border: 1px solid #334155; border-radius: 10px;
          background: #0f172a; color: white; box-sizing: border-box;
          transition: all 0.2s ease;
      }}
      input:focus {{ outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); }}
      button {{
          width: 100%; padding: 14px; background-color: var(--primary-color);
          color: white; border: none; border-radius: 10px; font-weight: 600;
          cursor: pointer; transition: background 0.3s ease, transform 0.1s ease;
      }}
      button:hover {{ background-color: var(--primary-hover); transform: translateY(-1px); }}
      button:active {{ transform: translateY(1px); }}
    </style>
    
    <script src="https://accounts.google.com/gsi/client" async defer></script>
    <script>
      function setMode(mode) {{
          document.getElementById('action').value = mode;
          document.getElementById('btn-login').classList.toggle('active', mode==='login');
          document.getElementById('btn-register').classList.toggle('active', mode==='register');
          document.getElementById('submit-btn').innerText = mode==='login' ? 'Ingresar' : 'Registrarse';
      }}
      function handleGoogleCredential(response) {{
          const form = document.createElement("form");
          form.method = "POST";
          form.action = "/login";
          const inputToken = document.createElement("input");
          inputToken.type = "hidden";
          inputToken.name = "google_token";
          inputToken.value = response.credential;
          
          const inputAction = document.createElement("input");
          inputAction.type = "hidden";
          inputAction.name = "action";
          inputAction.value = document.getElementById('action').value;
          
          form.appendChild(inputToken);
          form.appendChild(inputAction);
          document.body.appendChild(form);
          form.submit();
      }}
    </script>

    </head><body>
    <div class="login-box">
        <h2>IA-ATC</h2>
        {msg_html}
        <div class="tabs">
            <button class="tab-btn active" id="btn-login" onclick="setMode('login')">Ingresar</button>
            <button class="tab-btn" id="btn-register" onclick="setMode('register')">Registrarse</button>
        </div>
        
        <form method="POST" action="/login" id="login-form">
            <input type="hidden" id="action" name="action" value="login" />
            <input type="text" name="username" id="username" placeholder="Usuario" autocomplete="off" />

            <input type="password" name="password" id="password" placeholder="Contraseña" />
            <div style="display:flex; align-items:center; justify-content:center; gap:8px; margin-top:5px; margin-bottom:5px; font-size:13px; color:#94a3b8; user-select:none;">
                <input type="checkbox" name="remember" id="remember" value="yes" style="cursor:pointer; width:auto; margin:0;" checked>
                <label for="remember" style="cursor:pointer; margin:0;">Mantener sesión iniciada</label>
            </div>
            <button type="submit" id="submit-btn" style="margin-top: 15px; margin-bottom: 20px;">Ingresar</button>

            <div style="text-align: center; margin-bottom: 10px; font-size: 14px; color: #94a3b8;">o continúa con</div>
            <div id="g_id_onload"
                 data-client_id="572322137024-s9knspr9emg17mtg2g4bhferuj9frrp7.apps.googleusercontent.com"
                 data-context="use"
                 data-ux_mode="popup"
                 data-callback="handleGoogleCredential"
                 data-auto_prompt="false">
            </div>
            <div class="g_id_signin"
                 data-type="standard"
                 data-shape="rectangular"
                 data-theme="outline"
                 data-text="continue_with"
                 data-size="large"
                 data-logo_alignment="left"
                 style="display: flex; justify-content: center;">
            </div>

        </form>

    </div>
    </body></html>
    """

@app.get("/perfil", response_class=HTMLResponse)
async def perfil_panel(request: Request):
    """Personalización de Usuario."""
    if not verificar_sesion(request):
        return HTMLResponse(obtener_login_html(), status_code=200)

    import os
    if not os.path.exists("perfil.html"): return HTMLResponse("404: perfil.html no encontrado")
        
    with open("perfil.html", "r", encoding="utf-8") as f:
        html = f.read()

    usuario_sesion = obtener_usuario_sesion(request)
    prefs = usuario_sesion.get("preferencias_ui", {}) if usuario_sesion else {}
    

    
    # Botones Admin
    if es_admin(request):
        admin_btn = """<a href="/admin" class="nav-item" title="Panel Estadístico"><svg viewBox="0 0 24 24"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg></a>"""
        settings_btn = """<a href="/settings" class="nav-item" title="Personalizar Agente IA"><svg viewBox="0 0 24 24"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg></a>"""
        usuarios_btn = """<a href="/usuarios" class="nav-item" title="Panel de Usuarios"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg></a>"""
    else:
        admin_btn = ""
        settings_btn = ""
        usuarios_btn = ""
        
    html = html.replace("{admin_button}", admin_btn)
    html = html.replace("{settings_button}", settings_btn)
    html = html.replace("{usuarios_button}", usuarios_btn)

    return HTMLResponse(inyectar_tema_global(request, html))

@app.get("/settings", response_class=HTMLResponse)
async def settings_panel(request: Request):
    """Personalización de Agente y Base de Conocimiento."""
    if not es_admin(request):
        return HTMLResponse(obtener_login_html(), status_code=200)

    import os
    if not os.path.exists("settings.html"): return HTMLResponse("404: settings.html no encontrado")
        
    with open("settings.html", "r", encoding="utf-8") as f:
        html = f.read()

    try:
        with open("guia_respuestas.md", "r", encoding="utf-8") as f:
            guia_content = f.read()
    except Exception:
        guia_content = ""

    try:
        from pedidos_observer import NOTIFICACIONES_PROACTIVAS_ACTIVAS
        proact_activo = NOTIFICACIONES_PROACTIVAS_ACTIVAS
    except:
        proact_activo = False

    html = html.replace("{guia_content}", guia_content)
    html = html.replace("{color_global}", "#10b981" if BOT_GLOBAL_ACTIVO else "#ef4444")
    html = html.replace("{proactive_text}", "Desactivar Envíos" if proact_activo else "Activar Sistema Proactivo")
    html = html.replace("{proactive_color}", "#ef4444" if proact_activo else "#10b981")
    
    import glob
    pdfs_html = ""
    for pdf in glob.glob("*.pdf"):
        pdfs_html += f"<li class='pdf-list-item'><div style='display:flex;align-items:center;gap:0.5rem;'><svg class='icon-pdf' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><polyline points='14 2 14 8 20 8'/></svg> {pdf}</div> <button onclick=\"deletePdf('{pdf}')\" class='pdf-delete-btn'><svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M3 6h18'/><path d='M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6'/><path d='M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2'/></svg> Borrar</button></li>"
    
    html = html.replace("{lista_pdfs}", pdfs_html or "<li style='color:var(--text-muted);font-style:italic;padding:0.5rem;'>Ningún archivo PDF subido.</li>")
    
    usuario_sesion = obtener_usuario_sesion(request)
    prefs = usuario_sesion.get("preferencias_ui", {}) if usuario_sesion else {}
    html = html.replace("{bg_main}", prefs.get("bg_main", "#0f172a"))
    html = html.replace("{primary_color}", prefs.get("primary_color", "#717f7f"))
    html = html.replace("{accent_bg}", prefs.get("accent_bg", "#1e293b"))
    html = html.replace("{wallpaper}", prefs.get("wallpaper", ""))

    return HTMLResponse(inyectar_tema_global(request, html))

@app.get("/api/media/{media_id}")
async def get_media_endpoint(media_id: str, request: Request):
    from fastapi.responses import Response, RedirectResponse
    
    data = None
    mime = None
    if media_id in media_cache:
        data, mime = media_cache[media_id]
    else:
        try:
            from whatsapp_client import obtener_media_url, descargar_media
            url = await obtener_media_url(media_id)
            if url:
                data, mime = await descargar_media(url)
                if data:
                    media_cache[media_id] = (data, mime)
        except: pass
        
    if not data:
        # DEVUELVE UN PLACEHOLDER NATIVO POR DEFAULT en vez de 404 para evitar parpadeos y errores de javascript en el cliente
        return RedirectResponse("https://placehold.co/250x150?text=Media+Expirado", status_code=302)
        
    # SOPORTE ESTRICTO PARA VIDEOS/AUDIOS EN NAVEGADORES MOVILES (HTTP 206 Range Requests)
    # Safari (iOS) y Chrome Móvil exigen que el servidor responda rangos parciales
    range_header = request.headers.get("Range")
    if range_header and ("video" in mime or "audio" in mime):
        import re
        match = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end_val = match.group(2)
            tot_len = len(data)
            end = int(end_val) if end_val else tot_len - 1
            if end >= tot_len:
                end = tot_len - 1
            length = end - start + 1
            chunk = data[start:end + 1]
            headers = {
                "Content-Range": f"bytes {start}-{end}/{tot_len}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
            }
            return Response(content=chunk, status_code=206, headers=headers, media_type=mime)
            
    return Response(content=data, headers={"Accept-Ranges": "bytes"}, media_type=mime)

@app.get("/api/quick-replies")
def get_quick_replies(request: Request, line: str = None):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import cargar_quick_replies_bd
    return cargar_quick_replies_bd(line)

@app.post("/api/quick-replies")
def create_quick_reply(request: Request, data: dict):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import guardar_quick_reply_bd
    import uuid
    new_id = data.get("id") or str(uuid.uuid4())
    mensajes = data.get("mensajes", None)
    # Derive content (plain text preview) from first text message
    content = data.get("content", "")
    if not content and mensajes:
        first = mensajes[0]
        if isinstance(first, dict):
            content = first.get("content") or f"[{first.get('type','media')}]"
        else:
            content = str(first)
    guardar_quick_reply_bd(
        id_qr=new_id,
        titulo=data.get("title", ""),
        contenido=content,
        categoria=data.get("category", "General"),
        tipo=data.get("type", "text"),
        mensajes=mensajes,
        delay_ms=int(data.get("delay_ms", 1500)),
        etiquetas=data.get("etiquetas", []),
        line_id=data.get("line_id", "principal")
    )
    return {"status": "ok", "id": new_id}

@app.post("/api/quick-replies/upload-media")
async def qr_upload_media(request: Request, file: UploadFile = File(...)):
    """Sube un archivo de media (imagen/video/audio) para usar en quick replies."""
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    try:
        from whatsapp_client import subir_media
        content = await file.read()
        media_id = await subir_media(content, file.content_type, file.filename or "upload")
        if media_id and not media_id.startswith("ERROR_META:"):
            # Detect type from content_type
            ct = file.content_type or ""
            if "image" in ct:
                media_type = "image"
            elif "video" in ct:
                media_type = "video"
            elif "audio" in ct:
                media_type = "audio"
            else:
                media_type = "document"
            return {"ok": True, "media_id": media_id, "media_type": media_type, "filename": file.filename}
        return {"ok": False, "error": "No se pudo subir a Meta"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.delete("/api/quick-replies/{qr_id}")
def delete_quick_reply(request: Request, qr_id: str):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    if not es_admin(request):
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar")
    from firebase_client import eliminar_quick_reply_bd
    eliminar_quick_reply_bd(qr_id)
    return {"status": "ok"}

@app.post("/api/quick-replies/reorder")
def reorder_quick_replies(request: Request, payload: dict):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    if not es_admin(request):
        raise HTTPException(status_code=403, detail="Solo administradores pueden reordenar")
    from firebase_client import reordenar_quick_replies_bd
    orden_list = payload.get("order", [])
    reordenar_quick_replies_bd(orden_list)
    return {"status": "ok"}


@app.get("/api/backup/export")
async def export_backup(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import cargar_quick_replies_bd, cargar_etiquetas_bd, cargar_plantillas_bd
    data = {
        "quick_replies": cargar_quick_replies_bd(),
        "labels": cargar_etiquetas_bd(),
        "templates": cargar_plantillas_bd()
    }
    headers = {"Content-Disposition": "attachment; filename=backup_iatc.json"}
    return JSONResponse(content=data, headers=headers)

@app.post("/api/backup/import")
async def import_backup(request: Request, file: UploadFile = File(...)):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    try:
        content = await file.read()
        import json
        data = json.loads(content.decode("utf-8"))
        from firebase_client import guardar_quick_reply_bd, guardar_etiqueta_bd, guardar_plantilla_bd
        
        if "quick_replies" in data:
            for qr in data["quick_replies"]:
                if qr.get("id"):
                    guardar_quick_reply_bd(
                        id_qr=qr.get("id"),
                        titulo=qr.get("title", ""),
                        contenido=qr.get("content", ""),
                        categoria=qr.get("category", "General"),
                        tipo=qr.get("type", "text")
                    )
        
        if "labels" in data:
            for lb in data["labels"]:
                if lb.get("id"):
                    guardar_etiqueta_bd(
                        id_etiqueta=lb.get("id"),
                        nombre=lb.get("name", "Etiqueta"),
                        color=lb.get("color", "#000000")
                    )
                    
        return {"status": "ok", "message": "Importación exitosa"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/api/settings/save")
async def save_settings(request: Request, guia_content: str = Form(...)):
    if not es_admin(request):
        raise HTTPException(status_code=403, detail="No autorizado")

    with open("guia_respuestas.md", "w", encoding="utf-8") as f:
        f.write(guia_content)
        
    # Limpiamos caché del bot nativo para que levante los nuevos conocimientos
    import prompts
    prompts._GUIA_CACHE = ""

    return RedirectResponse(url="/settings?saved=true", status_code=303)

@app.post("/api/settings/upload_pdf")
async def upload_pdf(request: Request, pdf_file: UploadFile = File(...)):
    if not es_admin(request):
        return RedirectResponse(url="/login", status_code=303)
        
    if pdf_file.filename and pdf_file.filename.lower().endswith(".pdf"):
        content = await pdf_file.read()
        with open(pdf_file.filename, "wb") as f:
            f.write(content)
            
        import prompts
        prompts._GUIA_CACHE = ""
        return RedirectResponse(url="/settings?pdf=true", status_code=303)
    
    return RedirectResponse(url="/settings?error=true", status_code=303)

@app.get("/api/settings/delete_pdf/{filename}")
async def delete_pdf(request: Request, filename: str):
    if not es_admin(request):
        return RedirectResponse(url="/login", status_code=303)
        
    import os
    if filename.endswith(".pdf") and os.path.exists(filename):
        os.remove(filename)
        import prompts
        prompts._GUIA_CACHE = ""
        
    return RedirectResponse(url="/settings?deleted=true", status_code=303)

@app.post("/api/settings/toggle_proactive")
async def toggle_proactive(request: Request):
    if not es_admin(request):
        return RedirectResponse(url="/login", status_code=303)
    
    import pedidos_observer
    pedidos_observer.NOTIFICACIONES_PROACTIVAS_ACTIVAS = not pedidos_observer.NOTIFICACIONES_PROACTIVAS_ACTIVAS
    
    return RedirectResponse(url="/settings", status_code=303)

@app.get("/api/admin/backups/chats/download")
async def download_chats_backup(request: Request):
    if not es_admin(request):
        return HTMLResponse("Acceso denegado. Se requieren permisos de administrador.", status_code=403)
    
    import os
    from fastapi.responses import FileResponse
    zip_path = "ultimo_backup_chats.zip"
    
    if not os.path.exists(zip_path):
        return HTMLResponse("""
            <h3>Aún no hay ningún backup disponible.</h3>
            <p>El sistema genera el primer backup durante la madrugada.</p>
            <p>Si deseas forzar el backup ahora mismo, ejecuta <code>py backup_chats.py</code> en tu VPS.</p>
        """, status_code=404)
        
    return FileResponse(
        path=zip_path,
        filename="chats_backup_LOCAL.zip",
        media_type="application/zip"
    )

@app.get("/api/admin/pedidos_por_telefono")
async def api_pedidos_por_telefono(request: Request, num: str):
    if not verificar_sesion(request):
        return JSONResponse({"ok": False, "error": "No autenticado"}, status_code=401)
    
    from firebase_client import buscar_pedido_por_telefono
    try:
        # buscar_pedido_por_telefono hace limpieza del número y busca variantes, retornando hasta 5 pedidos
        pedidos = buscar_pedido_por_telefono(num)
        return {"ok": True, "pedidos": pedidos}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/api/admin/editar_pedido_rapido/{pedido_id}")
async def api_editar_pedido_rapido(request: Request, pedido_id: str):
    if not verificar_sesion(request):
        return JSONResponse({"ok": False, "error": "No autenticado"}, status_code=401)
    try:
        data = await request.json()
        payload = {}
        
        if "envioDepartamento" in data: payload["envioDepartamento"] = data["envioDepartamento"]
        if "envioProvincia" in data: payload["envioProvincia"] = data["envioProvincia"]
        if "envioDistrito" in data: payload["envioDistrito"] = data["envioDistrito"]
        
        if "prendas" in data and isinstance(data["prendas"], list):
            payload["prendas"] = data["prendas"]
            
        if not payload:
            return {"ok": False, "error": "Nada que actualizar"}
            
        from firebase_client import inicializar_firebase
        db = inicializar_firebase()
        from datetime import datetime, timezone
        payload["updatedAt"] = datetime.now(timezone.utc)
        
        db.collection("pedidos").document(pedido_id).update(payload)
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/admin", response_class=HTMLResponse)
async def panel_admin(request: Request):
    """Panel web de administración mejorado."""
    if not verificar_sesion(request):
        return HTMLResponse(obtener_login_html(), status_code=200)

    # ── Datos para el panel ──────────────────────────────
    import os
    if not os.path.exists("admin.html"): return HTMLResponse("404: admin.html no encontrado")
        
    with open("admin.html", "r", encoding="utf-8") as f:
        html = f.read()

    ahora       = datetime.utcnow()
    total       = len(sesiones)
    escalados   = [(n, s) for n, s in sesiones.items() if not s["bot_activo"] and s.get("escalado_en")]
    escalados.sort(key=lambda x: x[1]["escalado_en"], reverse=True)
    n_escalados = len(escalados)
    n_activos   = sum(1 for s in sesiones.values() if s["bot_activo"])

    # removed ──────────────────────────

    # Reemplazos
    html = html.replace("{pwd}", "")
    html = html.replace("{color_global}", "#10b981" if BOT_GLOBAL_ACTIVO else "#ef4444")
    html = html.replace("{class_btn_toggle}", "danger" if BOT_GLOBAL_ACTIVO else "")
    html = html.replace("{txt_btn_toggle}", "Apagar IA Global" if BOT_GLOBAL_ACTIVO else "Activar IA Global")
    html = html.replace("{total_sesiones}", str(total))
    html = html.replace("{bots_activos}", str(n_activos))
    html = html.replace("{humanos_requeridos}", str(n_escalados))
    # replaced
    
    return HTMLResponse(inyectar_tema_global(request, html))


@app.post("/admin/reactivar/{numero_wa}")
async def reactivar_bot(request: Request, numero_wa: str):
    """Reactiva el bot para un número específico y limpia la sesión."""
    if not verificar_sesion(request):
        return RedirectResponse(url="/login", status_code=303)

    if numero_wa in sesiones:
        # Reactivar el bot sin borrar el historial ni los datos del pedido vinculados
        sesiones[numero_wa]["bot_activo"] = True
        sesiones[numero_wa]["escalado_en"] = None
        sesiones[numero_wa]["motivo_escalacion"] = None
        sesiones[numero_wa]["ultima_actividad"] = datetime.utcnow()
        print(f"  [▶ Bot reactivado para {numero_wa} desde panel admin]")
        try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesiones[numero_wa])
        except: pass

    form_data = await request.form()
    redirect_url = form_data.get("redirect", "/admin")
    return RedirectResponse(url=redirect_url, status_code=303)

@app.post("/api/admin/pausar/{numero_wa}")
async def pausar_bot_manual(request: Request, numero_wa: str):
    """Pausa al bot de forma manual para un WA específico."""
    if not verificar_sesion(request):
        return RedirectResponse(url="/login", status_code=303)

    if numero_wa in sesiones:
        sesiones[numero_wa]["bot_activo"] = False
        sesiones[numero_wa]["escalado_en"] = datetime.utcnow()
        sesiones[numero_wa]["motivo_escalacion"] = "Intervención manual forzada"
        print(f"  [⏸ Bot pausado manualmente para {numero_wa}]")
        try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesiones[numero_wa])
        except: pass
        
    form_data = await request.form()
    redirect_url = form_data.get("redirect", f"/inbox/{numero_wa}")
    return RedirectResponse(url=redirect_url, status_code=303)


@app.post("/api/admin/upload_media")
async def admin_upload_media(file: UploadFile = File(...), mode: str = Form(None)):
    """Sube media directamente desde la interfaz Web a Meta Graph."""
    try:
        from whatsapp_client import subir_media
        content = await file.read()
        
        fallback_name = "upload.bin"
        final_mime = file.content_type or "application/octet-stream"
        
        if mode == "video":
            final_mime = "video/mp4"
            fallback_name = "upload.mp4"
        elif mode == "audio":
            final_mime = "audio/webm"
            fallback_name = "upload.webm"
            
        if final_mime:
            if "image" in final_mime: fallback_name = "upload.png"
            elif "video" in final_mime: fallback_name = "upload.mp4"
            elif "audio" in final_mime: fallback_name = "upload.ogg"

        # Conversion nativa WebM -> MP4 para WhatsApp Voice Notes
        if "webm" in final_mime.lower():
            import subprocess, os, tempfile
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            try:
                # Usar tmp para cross-platform compatibility
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_in:
                    tmp_in.write(content)
                    tmp_in_name = tmp_in.name
                tmp_out_name = tmp_in_name.replace(".webm", ".ogg")

                # Ejecutar FFMPEG (via imageio-ffmpeg PIP)
                result = subprocess.run([
                    ffmpeg_exe, '-y', '-i', tmp_in_name,
                    '-c:a', 'libopus', '-b:a', '24k',
                    tmp_out_name
                ], capture_output=True)
                
                if result.returncode == 0 and os.path.exists(tmp_out_name):
                    with open(tmp_out_name, "rb") as f_out:
                        content = f_out.read()
                    final_mime = "audio/ogg; codecs=opus"
                    fallback_name = "voice.ogg"
                else:
                    err_msg = result.stderr.decode('utf-8', 'ignore') if result.stderr else "ExitCode!=0"
                    print("FFMPEG fallback ignorado o error:", err_msg)
                    return {"ok": False, "error": f"FFMPEG Conversion Failed: {err_msg}"}
                    
                os.remove(tmp_in_name)
                if os.path.exists(tmp_out_name): os.remove(tmp_out_name)
            except Exception as ex:
                print(f"Error procesando audio con ffmpeg: {ex}")
                return {"ok": False, "error": f"FFMPEG Missing on server: {ex}"}

        # Conversion y estabilizacion nativa de Video a MP4 (H.264)
        # Esto soluciona los videos horizontales rotados (plancha la metadata a los pixeles)
        # y soluciona la pantalla blanca en web (porque convierte HEVC de iPhone/Samsung a H264)
        elif "video" in final_mime.lower() or file.filename.lower().endswith(('.mov', '.mp4', '.avi', '.mkv')):
            import subprocess, os, tempfile
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            ext = ".mp4" if "mp4" in final_mime else ".mov"
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_in:
                    tmp_in.write(content)
                    tmp_in_name = tmp_in.name
                
                tmp_out_name = tmp_in_name + "_out.mp4"
                
                # Transcodificar a H.264. Utiliza preset ultrafast para evitar timeouts.
                # IMPORTANTE: -threads 1 evita que FFMPEG detecte los 32 cores del host de Railway
                # y sature la memoria RAM (OOM Killer) con multiples buffers.
                result = subprocess.run([
                    ffmpeg_exe, '-y', '-hide_banner', '-loglevel', 'error', '-i', tmp_in_name,
                    '-vf', 'scale=w=min(854\\,iw):h=-2',
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '32', '-maxrate', '1.5M', '-bufsize', '3M', '-threads', '1',
                    '-pix_fmt', 'yuv420p', '-profile:v', 'baseline', '-level', '3.0',
                    '-c:a', 'aac', '-b:a', '64k',
                    '-movflags', '+faststart',
                    tmp_out_name
                ], capture_output=True)
                
                if result.returncode == 0 and os.path.exists(tmp_out_name):
                    with open(tmp_out_name, "rb") as f_out:
                        content = f_out.read()
                    final_mime = "video/mp4"
                    fallback_name = "upload.mp4"
                else:
                    err_msg = result.stderr.decode('utf-8','ignore') if result.stderr else ""
                    if result.returncode < 0:
                        err_msg += f" (Killed by OS, Signal {-result.returncode}, probably OOM/Memory Limit)"
                    print("FFMPEG video error crítico:", err_msg)
                    # Mostrar el error limpio, ya que loglevel error quita la basura
                    return {"ok": False, "error": f"Error FFMPEG: {err_msg[:200]}"}
                
                os.remove(tmp_in_name)
                if os.path.exists(tmp_out_name): os.remove(tmp_out_name)
            except Exception as ex:
                print(f"Error procesando video con ffmpeg: {ex}")

        # META ES ESTRICTO: El filename debe coincidir con el mime_type real
        safe_filename = fallback_name
        if "audio/ogg" in final_mime: safe_filename = "voice.ogg"
        elif "video/mp4" in final_mime: safe_filename = "video.mp4"
        elif "image/" in final_mime: safe_filename = "image.png"

        media_id = await subir_media(content, final_mime, safe_filename)
        
        if media_id and not media_id.startswith("ERROR"):
            # Meta no permite descargar media enviada por nosotros mismos.
            # Por lo que es de vital importancia guardarla en la cache para mostrarla en nuestro propio chat.
            media_cache[media_id] = (content, final_mime)
            return {"ok": True, "media_id": media_id}
        
        return {"ok": False, "error": f"Meta rechazó archivo: {media_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/admin/buscar_mensajes")
async def buscar_mensajes(q: str, request: Request):
    if not verificar_sesion(request):
        return {"ok": False, "error": "No autorizado"}
    
    q = q.lower().strip()
    if not q or len(q) < 2:
        return {"ok": True, "resultados": []}
    
    resultados = []
    
    # Mapa inverso: wa_id_miembro -> info del grupo al que pertenece
    # Para que busquedas de miembros de grupo redirijan al grupo reflejo
    miembro_a_grupo = {}
    for vg in global_groups:
        for m in vg.get("members", []):
            miembro_a_grupo[m] = {"grupo_id": vg.get("id"), "grupo_nombre": vg.get("name", "Grupo")}

    # Usar dict para evitar iteraciones conflictivas
    for wa_id, session in list(sesiones.items()):
        historial = session.get("historial", [])
        nombre = session.get("nombre_cliente", wa_id)
        
        matches_en_chat = []
        # Inverso para los más recientes
        for msg in reversed(historial):
            content = msg.get("content", "")
            if content and q in content.lower() and msg.get("role") != "system":
                idx = content.lower().find(q)
                start = max(0, idx - 25)
                end = min(len(content), idx + len(q) + 25)
                snippet = content[start:end].replace("\n", " ")
                if start > 0: snippet = "..." + snippet
                if end < len(content): snippet += "..."
                
                matches_en_chat.append({
                    "role": msg.get("role"),
                    "snippet": snippet,
                    "msg_id": msg.get("msg_id", "")
                })
                # Max 3 matches por chat para no saturar
                if len(matches_en_chat) >= 3:
                    break
        
        if matches_en_chat:
            # Si el wa_id es miembro de un grupo virtual, redirigir al grupo
            grupo_info = miembro_a_grupo.get(wa_id)
            if grupo_info:
                resultados.append({
                    "wa_id": grupo_info["grupo_id"],
                    "nombre": f"\U0001f465 {grupo_info['grupo_nombre']}",
                    "nombre_real": nombre,
                    "wa_id_origen": wa_id,
                    "matches": matches_en_chat
                })
            else:
                resultados.append({
                    "wa_id": wa_id,
                    "nombre": nombre,
                    "matches": matches_en_chat
                })
            
    return {"ok": True, "resultados": resultados}

@app.post("/api/admin/enviar_media_manual")
async def enviar_media_manual_endpoint(request: Request, wa_id: str = Form(...), file: UploadFile = File(...)):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")

    if wa_id not in sesiones:
        return {"ok": False, "error": "Chat no existe"}

    contents = await file.read()
    from whatsapp_client import subir_media, enviar_media
    import anyio
    
    media_id = await anyio.to_thread.run_sync(subir_media, contents, file.content_type, file.filename)
    if not media_id:
        return {"ok": False, "error": "Error comunicando con Meta para subir archivo"}
        
    tipo_msg = "document"
    if file.content_type.startswith("image/"): tipo_msg = "image"
    elif file.content_type.startswith("video/"): tipo_msg = "video"
    elif file.content_type.startswith("audio/"): tipo_msg = "audio"
    
    exito = await anyio.to_thread.run_sync(enviar_media, wa_id, tipo_msg, media_id)
    if exito:
        import time
        ts = int(time.time())
        txt_bot = f"[{tipo_msg}:{media_id}|{file.filename}]"
        sesiones[wa_id]["historial"].append({"role": "assistant", "content": txt_bot, "timestamp": ts, "status": "sent"})
        try: 
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(wa_id, sesiones[wa_id])
        except: pass
        return {"ok": True}
    else:
        return {"ok": False, "error": "Error enviando vía Meta"}

@app.get("/api/frequent_chats")
async def get_frequent_chats(request: Request):
    """Devuelve los 6 chats con más mensajes en su historial."""
    if not verificar_sesion(request): raise HTTPException(status_code=403, detail="No autorizado")
    chats = []
    for w_id, data in sesiones.items():
        if w_id == "system": continue
        nombre = w_id
        if "contacts" in data and data["contacts"]:
            nombre = data["contacts"][0].get("profile", {}).get("name", w_id)
        msg_count = len(data.get("historial", []))
        if msg_count > 0:
            chats.append({"wa_id": w_id, "nombre": nombre, "msg_count": msg_count})
    chats.sort(key=lambda x: x["msg_count"], reverse=True)
    return {"chats": chats[:6]}

@app.post("/api/message/star")
async def toggle_star_message(request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    wa_id = data.get("wa_id")
    msg_id = data.get("msg_id")
    if not wa_id or not msg_id: return {"ok": False, "error": "Datos incompletos"}
    
    s = sesiones.get(wa_id)
    if not s: return {"ok": False, "error": "Chat no encontrado"}
    
    found = False
    for m in s.get("historial", []):
        if m.get("msg_id") == msg_id:
            m["is_starred"] = not m.get("is_starred", False)
            found = True
            break
            
    if found:
        try:
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(wa_id, s)
        except Exception:
            pass
        return {"ok": True}
    return {"ok": False, "error": "Mensaje no encontrado"}

@app.post("/api/message/pin")
async def toggle_pin_message(request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    wa_id = data.get("wa_id")
    msg_id = data.get("msg_id")
    if not wa_id or not msg_id: return {"ok": False, "error": "Datos incompletos"}
    
    s = sesiones.get(wa_id)
    if not s: return {"ok": False, "error": "Chat no encontrado"}
    
    found = False
    for m in s.get("historial", []):
        if m.get("msg_id") == msg_id:
            m["is_pinned"] = not m.get("is_pinned", False)
            found = True
            break
            
    if found:
        try:
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(wa_id, s)
        except Exception:
            pass
        return {"ok": True}
    return {"ok": False, "error": "Mensaje no encontrado"}

@app.post("/api/forward_messages")
async def forward_messages(request: Request):
    """Reenvía mensajes de un chat origen a múltiples destinos."""
    if not verificar_sesion(request): raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    source_wa_id = data.get("source_wa_id")
    wamids = data.get("wamids", [])
    targets = data.get("targets", [])
    
    if not source_wa_id or not wamids or not targets:
        return {"ok": False, "error": "Datos incompletos"}
        
    s = sesiones.get(source_wa_id)
    if not s: return {"ok": False, "error": "Chat origen no encontrado"}
    
    msgs_to_forward = [m for m in s.get("historial", []) if m.get("msg_id") in wamids]
    if not msgs_to_forward: return {"ok": False, "error": "Mensajes no encontrados, recargue la web."}
    msgs_to_forward.sort(key=lambda x: x.get("timestamp", 0))
    
    from whatsapp_client import enviar_media, enviar_mensaje, subir_media
    import re
    import time
    from datetime import datetime
    
    usuario_sesion = obtener_usuario_sesion(request)
    sent_by_name = (usuario_sesion.get("nombre") or usuario_sesion.get("username", "Agente")) if usuario_sesion else "Agente"
    
    success_count = 0
    for target in targets:
        # limpiar posibles caracteres de separación humana (espacios, guiones)
        target = target.replace(" ", "").replace("+", "").replace("-", "")
        if len(target) == 9 and target.startswith("9"): target = "51" + target
        if not target.isdigit(): continue
        
        target_sesion = obtener_o_crear_sesion(target)
        
        for msg in msgs_to_forward:
            texto = msg.get("content", "")
            if not texto: continue
            
            partes = re.split(r'(\[(?:sticker|imagen|video|audio|sticker-local|documento):[^\]]+\])', texto)
            
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
                    elif match_audio:
                        w_id_current = enviar_media(target, "audio", match_audio.group(1))
                    elif match_sticker_local:
                        filename = match_sticker_local.group(1)
                        from firebase_client import obtener_sticker_de_bd
                        file_bytes = obtener_sticker_de_bd(filename)
                        if file_bytes:
                            mime = "image/webp" if filename.endswith(".webp") else "image/png"
                            w_id_meta = await subir_media(file_bytes, mime, filename)
                            if w_id_meta:
                                tipo = "sticker" if mime == "image/webp" else "image"
                                w_id_current = enviar_media(target, tipo, w_id_meta)
                    else: 
                        w_id_current = enviar_mensaje(target, p)
                except Exception as e:
                    print(f"Error reenviando mensaje a {target}: {e}")
                    continue
                
                if w_id_current:
                    target_sesion["historial"].append({"role": "assistant", "content": p, "msg_id": w_id_current, "status": "sent", "timestamp": int(time.time()), "sent_by": sent_by_name})
                    target_sesion["ultima_actividad"] = datetime.utcnow()
                    
        try:
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(target, target_sesion)
        except: pass
        success_count += 1
        
    return {"ok": True, "count": success_count}


@app.post("/api/admin/enviar_manual")
async def enviar_manual_endpoint(request: Request):
    """Recibe mensaje del panel web y lo despacha a WhatsApp nativamente."""
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    
    data = await request.json()
    wa_id = data.get("wa_id")
    texto = data.get("texto", "").strip()
    reply_to_wamid = data.get("reply_to_wamid")
    quick_reply_title = data.get("quick_reply_title", "")
    
    if not wa_id or wa_id not in sesiones or not texto:
        return {"ok": False}
        
    s = sesiones[wa_id]
    # No guardamos en historial todavía, hasta confirmar envío

    from whatsapp_client import enviar_mensaje, enviar_media
    import re
    
    # Extraer número real y línea desde la sesión (clave puede ser compuesta: line_numero)
    line_id = s.get("lineId", "principal") or "principal"
    # Si lineId es numérico (Meta ID), normalizar a "principal"
    if line_id.isdigit():
        line_id = "principal"
    
    numero_envio = s.get("numero_real")  # número real guardado explícitamente
    if not numero_envio:
        # Fallback: extraer número real desde la clave compuesta "lineId_numero"
        if "_" in wa_id:
            _parts = wa_id.rsplit("_", 1)
            if len(_parts) == 2 and _parts[1].isdigit():
                numero_envio = _parts[1]
        if not numero_envio:
            numero_envio = wa_id  # último recurso: usar wa_id tal cual

    async def process_and_send():
        from whatsapp_client import enviar_media, enviar_mensaje, subir_media
        partes = re.split(r'(\[(?:sticker|imagen|video|audio|sticker-local|documento):[^\]]+\])', texto)
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
            import urllib.parse
            if match_sticker: 
                w_id_current = enviar_media(numero_envio, "sticker", match_sticker.group(1), reply_to_wamid, line_id=line_id)
            elif match_img:
                cap = urllib.parse.unquote(match_img.group(2)) if match_img.group(2) else None
                w_id_current = enviar_media(numero_envio, "image", match_img.group(1), reply_to_wamid, caption=cap, line_id=line_id)
            elif match_video:
                cap = urllib.parse.unquote(match_video.group(2)) if match_video.group(2) else None
                w_id_current = enviar_media(numero_envio, "video", match_video.group(1), reply_to_wamid, caption=cap, line_id=line_id)
            elif match_doc:
                cap = urllib.parse.unquote(match_doc.group(2)) if match_doc.group(2) else None
                w_id_current = enviar_media(numero_envio, "document", match_doc.group(1), reply_to_wamid, caption=cap, line_id=line_id)
            elif match_audio:
                w_id_current = enviar_media(numero_envio, "audio", match_audio.group(1), reply_to_wamid, line_id=line_id)
            elif match_sticker_local:
                filename = match_sticker_local.group(1)
                from firebase_client import obtener_sticker_de_bd
                file_bytes = obtener_sticker_de_bd(filename)
                if file_bytes:
                    mime = "image/webp" if filename.endswith(".webp") else "image/png"
                    w_id_meta = await subir_media(file_bytes, mime, filename)
                    if w_id_meta:
                        tipo = "sticker" if mime == "image/webp" else "image"
                        w_id_current = enviar_media(numero_envio, tipo, w_id_meta, reply_to_wamid, line_id=line_id)
            else: 
                w_id_current = enviar_mensaje(numero_envio, p, reply_to_wamid, line_id=line_id)
            
            if w_id_current:
                last_wamid = w_id_current
                exito_alguna_parte = True
                
        return exito_alguna_parte, last_wamid

    # Wait for the API to process it synchronously from the user's perspective
    exito, msg_wamid = await process_and_send()
    
    if exito:
        import time
        ts = int(time.time())
        # Obtener usuario que envió el mensaje — usar nombre visible si está configurado
        usuario_sesion = obtener_usuario_sesion(request)
        sent_by_name = (usuario_sesion.get("nombre") or usuario_sesion.get("username", "Agente")) if usuario_sesion else "Agente"
        s["historial"].append({"role": "assistant", "content": texto, "msg_id": msg_wamid, "status": "sent", "timestamp": ts, "sent_by": sent_by_name, "quick_reply_title": quick_reply_title})
        s["ultima_actividad"] = datetime.utcnow()
        print(f"  [👤 Humano -> {numero_envio} ({line_id})]: {texto}")
        try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(wa_id, s)
        except: pass
        return {"ok": True}
    else:
        return {"ok": False, "error": "META_API_REJECTED"}


class ReaccionPayload(BaseModel):
    wa_id: str
    message_id: str
    emoji: str

@app.post("/api/admin/reaccionar")
async def admin_reaccionar(payload: ReaccionPayload, request: Request):
    """Permite al operador reaccionar a un mensaje del usuario."""
    if not verificar_sesion(request):
        return {"ok": False, "error": "No autorizado"}
    
    from whatsapp_client import enviar_reaccion_async
    exito = await enviar_reaccion_async(payload.wa_id, payload.message_id, payload.emoji)
    
    if exito:
        # Añadir al historial local? (Opcional, pero para mantener registro)
        s = sesiones.get(payload.wa_id)
        if s:
            s["historial"].append({"role": "assistant", "content": f"*[Reacción enviada: {payload.emoji}]*"})
            s["ultima_actividad"] = datetime.utcnow()
            try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(payload.wa_id, s)
            except: pass
        return {"ok": True}
    return {"ok": False, "error": "No se pudo enviar la reacción a Meta"}

@app.post("/admin/toggle")
async def toggle_bot_global(request: Request):
    """Activa o desactiva el bot globalmente."""
    global BOT_GLOBAL_ACTIVO
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    BOT_GLOBAL_ACTIVO = not BOT_GLOBAL_ACTIVO
    estado = "ACTIVADO" if BOT_GLOBAL_ACTIVO else "APAGADO"
    print(f"  [\u26a1 Bot {estado} globalmente desde panel admin]")
    return RedirectResponse(url=f"/admin", status_code=303)

@app.get("/api/debug/historial/{wa_id}")
async def debug_historial(wa_id: str):
    if wa_id in sesiones:
        return JSONResponse(sesiones[wa_id]["historial"])
    return {"status": "none"}



from fastapi.responses import Response


# ─────────────────────────────────────────────
#  Health check y Debug
# ─────────────────────────────────────────────


@app.get("/usuarios", response_class=HTMLResponse)
async def panel_usuarios(request: Request):
    if not es_admin(request):
        return RedirectResponse(url="/inbox", status_code=303)
        
    import os
    if not os.path.exists("usuarios.html"): return HTMLResponse("404: usuarios.html no encontrado")
        
    with open("usuarios.html", "r", encoding="utf-8") as f:
        html = f.read()

    admin_btn = """<a href="/admin" class="nav-item" title="Panel Estadístico"><svg viewBox="0 0 24 24"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg></a>"""
    settings_btn = """<a href="/settings" class="nav-item" title="Personalizar Agente IA"><svg viewBox="0 0 24 24"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg></a>"""
    usuarios_btn = """<a href="/usuarios" class="nav-item active" title="Panel de Usuarios"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg></a>"""
    
    html = html.replace("{admin_button}", admin_btn)
    html = html.replace("{settings_button}", settings_btn)
    html = html.replace("{usuarios_button}", usuarios_btn)
    html = html.replace("{color_global}", "#10b981" if BOT_GLOBAL_ACTIVO else "#ef4444")
    
    return HTMLResponse(inyectar_tema_global(request, html))

@app.get("/api/usuarios/list")
async def api_usuarios_list(request: Request):
    if not es_admin(request):
        return {"error": "Unauthorized"}
    from firebase_client import obtener_todos_los_usuarios
    return obtener_todos_los_usuarios()

@app.post("/api/usuarios/update")
async def api_usuarios_update(request: Request, data: dict):
    if not es_admin(request):
        return {"error": "Unauthorized"}
    from firebase_client import actualizar_permisos_usuario
    username = data.get("username")
    estado = data.get("estado")
    permisos = data.get("permisos", [])
    nombre = data.get("nombre", "")
    if actualizar_permisos_usuario(username, estado, permisos, nombre):
        for token, user in active_sessions.items():
            if user.get("username") == username:
                user["nombre"] = nombre
                break
        return {"ok": True}
    return {"ok": False}

@app.get("/")

async def home_redirect():
    return RedirectResponse("/inbox", status_code=303)

@app.get("/health")
async def health():
    return {"status": "ok", "bot": "IA-ATC", "sesiones": len(sesiones)}

@app.get("/debug_err", response_class=HTMLResponse)
async def debug_error():
    import os
    if os.path.exists("error_gemini.txt"):
        with open("error_gemini.txt", "r") as f:
            return f"<pre>{f.read()}</pre>"
    return "No hay error_gemini.txt registrado."


@app.get("/admin/chat/{numero_wa}", response_class=HTMLResponse)
async def ver_chat(request: Request, numero_wa: str):
    """Vista de conversación estilo WhatsApp para un número específico."""
    if not verificar_sesion(request):
        return RedirectResponse(url=f"/admin", status_code=302)

    sesion = sesiones.get(numero_wa)
    if not sesion:
        return HTMLResponse("<h2 style='font-family:sans-serif;padding:2rem'>Sesión no encontrada o ya expiró.</h2>")

    nombre  = sesion.get("nombre_cliente", numero_wa)
    pedido  = sesion.get("datos_pedido", {}).get("id", "—") if sesion.get("datos_pedido") else "—"
    estado  = sesion.get("datos_pedido", {}).get("estadoGeneral", "—") if sesion.get("datos_pedido") else "—"
    activo  = sesion.get("bot_activo", True)
    msgs    = [m for m in sesion.get("historial", []) if m["role"] != "system"]

    burbujas = ""
    pinned_messages = []
    for m in msgs:
        es_bot    = m["role"] == "assistant"
        clase     = "burbuja-bot" if es_bot else "burbuja-user"
        lado      = "bot-lado" if es_bot else "user-lado"
        remitente = "🤖 María" if es_bot else f"👤 {nombre}"
        texto     = m["content"].replace("\n", "<br>")
        def wrap_phone(match):
            phone = match.group(1)
            clean_phone = __import__('re').sub(r'[\s\-]', '', phone)
            if sum(c.isdigit() for c in clean_phone) >= 7:
                return f'<span class="chat-phone" style="text-decoration:underline; cursor:pointer; font-weight:bold;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
            return phone
        texto = __import__('re').sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)
        burbujas += f"""
        <div class="mensaje {lado}">
          <div class="remitente">{remitente}</div>
          <div class="{clase}">{texto}</div>
        </div>"""

    if not burbujas:
        burbujas = '<p style="text-align:center;color:#aaa;padding:2rem">Sin mensajes aún en esta sesión</p>'

    estado_badge = "🟢 Bot activo" if activo else "🔴 Esperando humano"
    color_badge  = "#2e7d32" if activo else "#c62828"
    bg_badge     = "#e8f5e9" if activo else "#ffebee"

    btn_reactivar = "" if activo else f"""
    <form method="post" action="/admin/reactivar/{numero_wa}" style="margin:0">
      <button style="background:#25d366;color:white;border:none;padding:.5rem 1rem;
                     border-radius:8px;cursor:pointer;font-weight:600">▶ Reactivar bot</button>
    </form>"""

    return HTMLResponse(f"""
    <html><head><title>Chat: {nombre}</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
      :root {{
        --wa-bg: #ece5dd;
        --wa-chat-bg: #e5ddd5;
        --wa-header: #075e54;
        --wa-me: #dcf8c6;
        --wa-bot: #ffffff;
        --text-dark: #111b21;
        --text-gray: #667781;
      }}
      *{{box-sizing:border-box;margin:0;padding:0}}
      body{{font-family:'Inter',sans-serif;background-color:var(--wa-chat-bg);
            /* Patrón sutil de fondo tipo WhatsApp */
            background-image: url('data:image/svg+xml,%3Csvg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath d="M20 20.5V18H0v-2h20v-2H0v-2h20v-2H0V8h20V6H0V4h20V2H0V0h22v20h2V0h2v20h2V0h2v20h2V0h2v20h2V0h2v20h2v2H20v-1.5zM0 20h2v20H0V20zm4 0h2v20H4V20zm4 0h2v20H8V20zm4 0h2v20h-2V20zm4 0h2v20h-2V20zm4 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2z" fill="%23dfd8d1" fill-opacity="0.4" fill-rule="evenodd"/%3E%3C/svg%3E');
            min-height:100vh;display:flex;flex-direction:column;
            -webkit-font-smoothing: antialiased;}}
      .topbar{{background:var(--wa-header);color:white;padding:1rem 1.5rem;
               display:flex;justify-content:space-between;align-items:center;
               box-shadow:0 2px 4px rgba(0,0,0,.1);position:sticky;top:0;z-index:10}}
      .topbar-left h2{{font-size:1.1rem;font-weight:600;margin-bottom:.15rem}}
      .topbar-left small{{font-size:.85rem;opacity:.9}}
      .topbar-right{{display:flex;align-items:center;gap:1rem}}
      .estado-chip{{padding:.35rem .85rem;border-radius:20px;font-size:.8rem;font-weight:600;
                    background:{bg_badge};color:{color_badge};border:1px solid rgba(0,0,0,0.05)}}
      .btn-reactivar{{background:#25d366;color:white;border:none;padding:.5rem 1rem;
                      border-radius:8px;cursor:pointer;font-weight:600;font-size:.85rem;
                      transition:transform .2s, box-shadow .2s;box-shadow:0 1px 2px rgba(0,0,0,0.1)}}
      .btn-reactivar:hover{{transform:translateY(-1px);box-shadow:0 4px 6px rgba(0,0,0,0.15)}}
      .back-btn{{color:white;text-decoration:none;font-size:.9rem;font-weight:500;
                 background:rgba(255,255,255,.15);padding:.5rem 1rem;border-radius:8px;
                 transition:background .2s}}
      .back-btn:hover{{background:rgba(255,255,255,.25)}}
      .chat-area{{flex:1;padding:1.5rem;display:flex;flex-direction:column;gap:.75rem;max-width:850px;
                  width:100%;margin:0 auto}}
      .mensaje{{display:flex;flex-direction:column;max-width:80%;position:relative}}
      .bot-lado{{align-self:flex-start}}
      .user-lado{{align-self:flex-end}}
      .remitente{{font-size:.75rem;color:var(--text-gray);margin-bottom:.25rem;font-weight:600}}
      .user-lado .remitente{{text-align:right}}
      .burbuja-bot{{background:var(--wa-bot);border-radius:0 12px 12px 12px;padding:.75rem 1rem;
                   font-size:.95rem;line-height:1.45;box-shadow:0 1px 2px rgba(0,0,0,.1);
                   color:var(--text-dark);position:relative}}
      .burbuja-user{{background:var(--wa-me);border-radius:12px 0 12px 12px;padding:.75rem 1rem;
                    font-size:.95rem;line-height:1.45;box-shadow:0 1px 2px rgba(0,0,0,.1);
                    color:var(--text-dark);position:relative}}
      /* Colitas de las burbujas */
      .burbuja-bot::before{{content:"";position:absolute;top:0;left:-8px;
                            border-right:8px solid var(--wa-bot);border-bottom:8px solid transparent}}
      .burbuja-user::before{{content:"";position:absolute;top:0;right:-8px;
                             border-left:8px solid var(--wa-me);border-bottom:8px solid transparent}}
                             
      .info-bar{{background:white;margin:1.5rem auto 0;border-radius:12px;padding:1rem 1.5rem;
                 display:flex;gap:2rem;font-size:.9rem;color:var(--text-gray);flex-wrap:wrap;
                 box-shadow:0 2px 5px rgba(0,0,0,.05);max-width:850px;width:calc(100% - 3rem);
                 border:1px solid rgba(0,0,0,0.02)}}
      .info-bar span{{display:flex;align-items:center;gap:.5rem}}
      .info-bar b{{color:var(--text-dark);font-weight:600}}
    </style></head>
    <body>
    <div class="topbar">
      <div class="topbar-left">
        <h2>{nombre}</h2>
        <small>+{numero_wa} &middot; Pedido #{pedido} &middot; {estado}</small>
      </div>
      <div class="topbar-right">
        <span class="estado-chip">{estado_badge}</span>
        {btn_reactivar.replace('button style="background:#25d366;color:white;border:none;padding:.5rem 1rem;\\n                     border-radius:8px;cursor:pointer;font-weight:600"', 'button class="btn-reactivar"')}
        <a href="/admin" class="back-btn">← Volver al Panel</a>
      </div>
    </div>
    <div class="info-bar">
      <span>👤 <b>{nombre}</b></span>
      <span>📦 Pedido <b>#{pedido}</b></span>
      <span>📌 Estado <b>{estado}</b></span>
      <span>💬 <b>{len(msgs)}</b> mensajes</span>
    </div>
    <div class="chat-area">
      {burbujas}
    </div>
    </body></html>
    """)

# ==========================================
# INBOX MODERNO (Tipo Respond.io / SPA)
# ==========================================

def renderizar_inbox(request: Request, wa_id: str = None, tab: str = "all", label_filter: str = None, unread: str = None, line_filter: str = "all"):
    import json
    aliases = {}
    try:
        with open("line_aliases.json", "r", encoding="utf-8") as f:
            aliases = json.load(f)
    except: pass
    
    import os
    # Si estamos en Vercel (servidor sin estado fraccionado), forzamos lectura de BD para el chat activo actual
    if wa_id and os.environ.get("VERCEL"):
        try:
            from firebase_client import cargar_sesion_chat
            s_db = cargar_sesion_chat(wa_id)
            if s_db:
                sesiones[wa_id] = s_db
        except Exception:
            pass
    # Si las etiquetas están vacías por un hot-reload fallido, recuperarlas
    global global_labels
    if not global_labels:
        try:
            from firebase_client import cargar_etiquetas_bd
            global_labels = cargar_etiquetas_bd()
        except: pass

    global global_groups
    if not global_groups:
        try:
            from firebase_client import cargar_grupos_bd
            global_groups = cargar_grupos_bd()
        except: pass

    if not verificar_sesion(request):
        return HTMLResponse(obtener_login_html(), status_code=401)

    import os
    if not os.path.exists("inbox.html"): return HTMLResponse("404: inbox.html no encontrado")
        
    
    with open("inbox.html", "r", encoding="utf-8") as f:
        html = f.read()

    if not es_admin(request):
        import re
        html = re.sub(r'<a href="/settings".*?</a>', '', html, flags=re.DOTALL)
        html = re.sub(r'<a href="/admin".*?</a>', '', html, flags=re.DOTALL)
        html = re.sub(r'<a href="/usuarios".*?</a>', '', html, flags=re.DOTALL)

    es_admin_str = "true" if es_admin(request) else "false"
    html = html.replace("<style id=\"custom-theme-css\">", f"<script>window.ES_ADMIN = {es_admin_str};</script><style id=\"custom-theme-css\">")

    labels_ctx_html = ""
    for l in global_labels:
        labels_ctx_html += f'<div style="padding:0.6rem 1rem; color:var(--text-main); font-size:0.85rem; cursor:pointer; display:flex; align-items:center; gap:0.5rem; transition:background 0.2s;" onmouseover="this.style.background=\'var(--accent-hover)\'" onmouseout="this.style.background=\'transparent\'" onclick="window.chatActionLabel(\'{l.get("id")}\'); return false;"><div style="width:10px;height:10px;border-radius:50%;background:{l.get("color", "#ccc")};"></div> {l.get("name")}</div>'
    
    if not labels_ctx_html:
        labels_ctx_html = '<div style="padding:0.6rem 1rem; color:var(--text-muted); font-size:0.85rem; text-align:center;">Sin etiquetas globales</div>'

    html = html.replace("<!-- LABEL_CONTEXT_INJECTION -->", labels_ctx_html)

    ahora = datetime.utcnow()
    
    def tiempo_relativo(dt):
        diff = ahora - dt
        m = int(diff.total_seconds() / 60)
        if m < 1:   return "ahora"
        if m < 60:  return f"{m}m"
        if m < 1440: return f"{m//60}h"
        return f"{m//1440}d"

    def ultimo_msg(sesion):
        hist = [m for m in sesion.get("historial", []) if m["role"] != "system"]
        if not hist: return "—"
        return hist[-1]["content"][:50] + ("…" if len(hist[-1]["content"]) > 50 else "")

    # Procesar Lista de Chats
    grupos_sesiones = []
    for vg in global_groups:
        miembros = vg.get("members", [])
        sesiones_miembros = [sesiones.get(m) for m in miembros if m in sesiones]
        if not sesiones_miembros: continue
        vg_ultima_actividad = max((s.get("ultima_actividad", datetime.utcnow()) for s in sesiones_miembros))
        
        hist_total = []
        for s in sesiones_miembros:
            hist_total.extend(s.get("historial", []))
        hist_total.sort(key=lambda x: str(x.get("timestamp", "")))
        
        s_fake = {
            "ultima_actividad": vg_ultima_actividad,
            "nombre_cliente": f"{vg.get('name')}",
            "bot_activo": True,
            "historial": hist_total[-50:],
            "is_virtual_group": True,
            "vg_id": vg.get("id"),
            "etiquetas": [],
            "is_pinned": vg.get("is_pinned", False),
            "is_archived": vg.get("is_archived", False)
        }
        grupos_sesiones.append((vg.get("id"), s_fake))

    # Reset unread count for active chat ONLY IF it's not an AJAX poll.
    # When the user clicks a chat, the browser navigates to `/inbox/{wa_id}` (not ajax).
    # When the sidebar updates in the background, it appends `?ajax=1`.
    is_ajax = request.query_params.get("ajax") == "1"
    if wa_id and wa_id in sesiones and not is_ajax:
        if sesiones[wa_id].get("unread_count", 0) != 0:
            sesiones[wa_id]["unread_count"] = 0
            try:
                from firebase_client import guardar_sesion_chat
                guardar_sesion_chat(wa_id, sesiones[wa_id])
            except: pass

    todas = sorted(list(sesiones.items()) + grupos_sesiones, key=lambda x: (x[1].get("is_pinned", False), x[1].get("ultima_actividad", datetime.min)), reverse=True)
    lista_chats_html = ""
    
    # ------------------ Generador de Filtro de Etiquetas HTML ------------------
    active_label_obj = next((l for l in global_labels if l.get("id") == label_filter), None) if label_filter else None
    active_label_name = active_label_obj.get("name") if active_label_obj else "Filtro: Ninguno"
    if active_label_name.endswith("Ninguno"): active_label_name = "Filtrar Etiquetas: Desactivado"

    base_url = f"/inbox/{wa_id}" if wa_id else "/inbox"
    is_unread = (unread == "true")
    unread_btn_bg = "var(--primary-color)" if is_unread else "var(--accent-bg)"
    unread_btn_text = "white" if is_unread else "var(--text-main)"

    
    # Parsear aliases que pueden ser strings (antiguos) u objetos (nuevos meta options)
    parsed_aliases = {}
    for k, v in aliases.items():
        if isinstance(v, dict):
            parsed_aliases[k] = v.get("name", k)
        else:
            parsed_aliases[k] = v

    active_line_name = "Todas las Líneas"
    if line_filter != "all":
        active_line_name = parsed_aliases.get(line_filter, "Línea Secundaria" if line_filter != "principal" else "Línea Principal")

    labels_filter_html = f"""
    <div style="position:relative; margin-top:1rem; text-align:left; display:flex; gap:0.5rem; align-items:center;">
        
        <button type="button" onclick="const m = document.getElementById('inboxLineMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:var(--text-main); font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            {active_line_name}
        </button>

        <div id="inboxLineMenu" style="display:none; position:absolute; top:calc(100% + 0.5rem); left:0; width:100%; max-width:250px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:8px; box-shadow:0 8px 16px rgba(0,0,0,0.5); flex-direction:column; z-index:100; overflow:hidden;">
            <a href="{base_url}?tab={tab}&label={label_filter or ''}&unread={unread or ''}&line=all" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{'var(--primary-color)' if line_filter == 'all' else 'transparent'};">Todas las Líneas</a>
            <a href="{base_url}?tab={tab}&label={label_filter or ''}&unread={unread or ''}&line=principal" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{'var(--primary-color)' if line_filter == 'principal' else 'transparent'};">Línea Principal</a>
"""
    for q_id, q_name in parsed_aliases.items():
        labels_filter_html += f'<a href="{base_url}?tab={tab}&label={label_filter or ""}&unread={unread or ""}&line={q_id}" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{"var(--primary-color)" if line_filter == q_id else "transparent"};">{q_name}</a>'
        
    labels_filter_html += "</div>"

    labels_filter_html += f"""
        <button type="button" onclick="const m = document.getElementById('inboxFilterMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:var(--text-main); font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
            {active_label_name}
        </button>
        
        <a href="{base_url}?tab={tab}&label={label_filter or ''}&unread={'false' if is_unread else 'true'}" style="background:{unread_btn_bg}; border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:{unread_btn_text}; font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600; text-decoration:none;">
            No leídos
        </a>
        
        <div id="inboxFilterMenu" style="display:none; position:absolute; top:calc(100% + 0.5rem); left:0; width:100%; max-width:250px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:8px; box-shadow:0 8px 16px rgba(0,0,0,0.5); flex-direction:column; z-index:100; overflow:hidden;">
            <a href="{base_url}?tab={tab}&unread={unread or ''}" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{'var(--primary-color)' if not label_filter else 'transparent'};">Todas (Sin filtro)</a>
    """
    
    for l in global_labels:
        lid = l.get("id")
        lnombre = l.get("name", "Etiqueta")
        lcolor = l.get("color", "#94a3b8")
        is_active = (label_filter == lid)
        bg = f"{lcolor}33" if is_active else "transparent"
        labels_filter_html += f"""
            <a href="{base_url}?tab={tab}&label={lid}&unread={unread or ''}" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; gap:0.6rem; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{bg};">
                <span style="width:12px; height:12px; border-radius:50%; background:{lcolor};"></span> {lnombre}
            </a>
        """
        
    labels_filter_html += '</div></div>'
    
    for num, s in todas:
        inactivo_horas = (ahora - s["ultima_actividad"]).total_seconds() / 3600
        activo = s.get("bot_activo", True)
        is_archived = s.get("is_archived", False)
        
        # ── Lógica de línea ──────────────────────────────────────────────────
        # 1. Si la CLAVE tiene formato numérico_número (ej: "984944321377299_51913048384"),
        #    es una sesión corrupta del bug breve → saltar.
        #    Estas NO son las sesiones normales; son duplicados innecesarios.
        _key_parts = num.split("_", 1)
        if len(_key_parts) == 2 and _key_parts[0].isdigit() and _key_parts[1].isdigit():
            continue  # Sesión corrupta compuesta por phone_number_id numérico — ignorar

        # 2. Determinar la línea de la sesión
        ch_line_raw = s.get("lineId", "") or ""

        # 3. Si lineId es un ID numérico de Meta (principal) → normalizar a "principal"
        if ch_line_raw and ch_line_raw.isdigit():
            ch_line_raw = "principal"
            s["lineId"] = "principal"  # corregir en RAM para futuras consultas

        # 4. Si lineId no está, intentar inferirlo desde la clave compuesta "nombre_número"
        if not ch_line_raw and "_" in num:
            _p = num.rsplit("_", 1)
            if len(_p) == 2 and _p[1].isdigit() and not _p[0].isdigit():
                ch_line_raw = _p[0]
                s["lineId"] = ch_line_raw
        # ─────────────────────────────────────────────────────────────────────
        
        # Filtro de Tab
        if tab == "archived":
            if not is_archived: continue
        else:
            if is_archived: continue
            if tab == "human" and activo:
                continue
            
        session_tags = s.get("etiquetas", [])
        if session_tags is None: session_tags = []
        
        # Filtro de Etiqueta (Label)
        if label_filter and label_filter not in session_tags:
            continue
            
        # Filtro de No leídos (Verifica si el último mensaje lo envió el usuario)
        if is_unread:
            hist_sin_sys = [m for m in s.get("historial", []) if m["role"] != "system"]
            if not hist_sin_sys or hist_sin_sys[-1]["role"] != "user":
                continue
                
        # FILTRO DE LINEA MULTIPLE
        ch_line = ch_line_raw or "principal"
        if line_filter != "all" and ch_line != line_filter:
            continue
            
        line_alias = parsed_aliases.get(ch_line, "Línea Secundaria" if ch_line != "principal" else "")
        badge_line = f'<span style="font-size:0.65rem; background:rgba(255,255,255,0.05); padding:2px 6px; border-radius:4px; margin-left:0.5rem; border:1px solid rgba(255,255,255,0.1); color:var(--text-muted);">{line_alias}</span>' if ch_line != "principal" else ""


        # Para claves compuestas (line_id_numero), extraer el número real para mostrar
        numero_display = s.get("numero_real", num)
        nombre   = s.get("nombre_cliente", numero_display)
        if not nombre: nombre = numero_display
        preview  = ultimo_msg(s)
        time_str = tiempo_relativo(s["ultima_actividad"])
        
        is_vg = s.get("is_virtual_group", False)
        if is_vg:
            badge_html = '<span class="badge" style="background:rgba(168, 85, 247, 0.15); color:#a855f7; border: 1px solid rgba(168, 85, 247, 0.3);">👥 GRUPO VIRTUAL</span>'
        else:
            badge_html = '<span class="badge">🟢 Bot Activo</span>'
            if not activo:
                badge_html = '<span class="badge badge-alert">🔴 Esperando</span>'
            
        active_class = "active-row" if wa_id == num else ""
            
        tags_html = ""
        if session_tags:
            tags_html = '<div style="display:flex; gap:0.3rem; margin-top:0.3rem; flex-wrap:wrap;">'
            for tid in session_tags:
                lbl = next((l for l in global_labels if l.get("id") == tid), None)
                if lbl:
                    col = lbl.get("color", "#94a3b8")
                    nm = lbl.get("name", "Etiqueta")
                    tags_html += f'<span style="background:{col}22; color:{col}; font-size:0.65rem; padding:0.15rem 0.4rem; border-radius:4px; font-weight:600; border: 1px solid {col}44;">{nm}</span>'
            tags_html += '</div>'
            
        extra_params = f"?tab={tab}"
        if label_filter: extra_params += f"&label={label_filter}"
        if unread: extra_params += f"&unread={unread}"
        
        is_pinned = s.get("is_pinned", False)
        pin_html = '<svg width="12" height="12" viewBox="0 0 24 24" fill="var(--primary-color)" style="margin-right:4px;"><path d="M16 3H8a1 1 0 0 0-1 1v5.586a1 1 0 0 1-.293.707l-2.414 2.414A1 1 0 0 0 5 13.414V19a1 1 0 0 0 1 1h5v3l1 2 1-2v-3h5a1 1 0 0 0 1-1v-5.586a1 1 0 0 0-.293-.707l-2.414-2.414A1 1 0 0 1 16 9.586V4a1 1 0 0 0-1-1z"/></svg>' if is_pinned else ''
        
        unread_count = s.get("unread_count", 0)
        unread_html = ""
        if unread_count == -1: # Indicador sin número (marcado manual)
            unread_html = '<div style="width:10px; height:10px; border-radius:50%; background:var(--primary-color); flex-shrink:0;"></div>'
        elif unread_count > 0:
            unread_html = f'<div style="min-width:20px; height:20px; border-radius:10px; background:var(--primary-color); color:var(--bg-main); font-size:0.75rem; font-weight:bold; display:flex; align-items:center; justify-content:center; padding:0 6px; flex-shrink:0;">{unread_count}</div>'
            
        lista_chats_html += f"""
        <a href="/inbox/{num}{extra_params}" class="chat-row {active_class}" oncontextmenu="if(window.showChatMenu) window.showChatMenu(event, '{num}', {'true' if is_archived else 'false'}, {'true' if is_pinned else 'false'}, {'true' if activo else 'false'}); return false;">
            <div style="display:flex; align-items:center; gap:0.5rem; justify-content:space-between;">
                <div style="flex:1; min-width:0; margin-right: 0.5rem;">
                    <div class="chat-row-header">
                        <span class="chat-name">{pin_html}{nombre}{badge_line}</span>
                        <span class="chat-time">{time_str}</span>
                    </div>
                    <div class="chat-preview">{preview}</div>
                    <div class="chat-badges">{badge_html}</div>
                    {tags_html}
                </div>
                {unread_html}
            </div>
        </a>"""

    if not lista_chats_html:
        lista_chats_html = '<div style="padding:2rem;text-align:center;color:var(--text-muted);font-size:0.9rem">No hay conversacioes que coincidan con estos filtros.</div>'

    # Procesar Panel Derecho (Chat Viewer)
    chat_viewer_html = ""
    chat_view_css = ""
    s_fake_vg = None
    
    if wa_id and wa_id.startswith("vg_"):
        vg = next((g for g in global_groups if g.get("id") == wa_id), None)
        if vg:
            s_fake_vg = {
                "is_virtual_group": True,
                "nombre_cliente": f"👥 {vg.get('name')}",
                "historial": [],
                "bot_activo": True,
                "ultima_actividad": datetime.utcnow()
            }
            miembros = vg.get("members", [])
            for m in miembros:
                if m in sesiones:
                    hist = sesiones[m].get("historial", [])
                    nombre_m = sesiones[m].get("nombre_cliente") or m
                    for msg in hist:
                        msg_copy = dict(msg)
                        msg_copy["sender_name_override"] = nombre_m
                        msg_copy["sender_wa_id"] = m
                        s_fake_vg["historial"].append(msg_copy)
            s_fake_vg["historial"].sort(key=lambda x: str(x.get("timestamp", "")))
            
            if not s_fake_vg["historial"]:
                chat_viewer_html = f'''<div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--text-muted);font-size:0.95rem;flex-direction:column;gap:10px;">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    <p>Grupo Virtual "{vg.get('name')}".</p><p>Todavía no hay mensajes correspondientes a sus miembros.</p>
                </div>'''

    # Auto-inicializar chat nuevo si se manda un número válido (ej. desde el buscador UI)
    elif wa_id and wa_id not in sesiones:
        import re
        if re.match(r'^51\d{9}$', str(wa_id)):
            sesiones[wa_id] = {
                "historial": [],
                "ultima_actividad": datetime.utcnow(),
                "bot_activo": False,
                "nombre_cliente": f"+{wa_id}"
            }
            # Add to the left side menu as well right now so it renders
            todas.insert(0, (wa_id, sesiones[wa_id]))

    elif wa_id and (wa_id in sesiones) and len(sesiones[wa_id].get("historial", [])) == 0:
        chat_viewer_html = f'''<div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--text-muted);font-size:0.95rem;flex-direction:column;gap:10px;">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <p>Nuevo chat inicializado.</p><p>Escribe tu primer mensaje abajo para saludar a <b>+{wa_id}</b>.</p>
        </div>'''
        
    if not wa_id or (wa_id not in sesiones and not s_fake_vg):
        chat_viewer_html = """
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <h3>Tu Inbox está vacío</h3>
            <p>Selecciona una conversación a la izquierda o navega por números nuevos.</p>
        </div>"""
    else:
        # Renderizar Chat Activo
        s = s_fake_vg if s_fake_vg else sesiones[wa_id]
        nombre_chat = s.get("nombre_cliente", s.get("numero_real", wa_id))
        numero_chat_display = s.get("numero_real", wa_id)  # número real sin prefijo de línea
        activo_chat = s.get("bot_activo", True)
        all_msgs = [m for m in s.get("historial", []) if m["role"] != "system"]
        
        load_all = request.query_params.get("history") == "all" or bool(request.query_params.get("msg_id"))
        MAX_MENSAJES = 70
        msgs = all_msgs if load_all else all_msgs[-MAX_MENSAJES:]
        
        import re
        burbujas = ""
        pinned_messages = []
        starred_messages = []
        if len(all_msgs) > MAX_MENSAJES and not load_all:
            burbujas = f'<div style="text-align:center; opacity:0.8; margin: 1rem 0; font-size:0.8rem; background:var(--accent-bg); padding:0.6rem; border-radius:8px; border:1px solid var(--accent-border);">Mostrando últimos {MAX_MENSAJES} de {len(all_msgs)} mensajes.<br><button type="button" onclick="window.location.href = window.location.href + (window.location.href.includes(\'?\') ? \'&\' : \'?\') + \'history=all\';" style="background:var(--primary-color);color:white;border:none;padding:0.3rem 0.8rem;border-radius:6px;font-weight:600;cursor:pointer;margin-top:0.4rem;transition:background 0.2s;">📥 Cargar historial completo ([WARN] Más lento)</button></div>'
        last_date_str = ""
        for m in msgs:
            # Insertar separador de fecha si cambia el día
            ts_unix = m.get("timestamp", "")
            date_str = ""
            if ts_unix:
                try:
                    ts_val = int(ts_unix)
                    if ts_val > 1e11: ts_val //= 1000
                    lima_dt = datetime.utcfromtimestamp(ts_val) - timedelta(hours=5)
                    today_dt = datetime.utcnow() - timedelta(hours=5)
                    
                    if lima_dt.date() == today_dt.date():
                        date_str = "Hoy"
                    elif lima_dt.date() == (today_dt - timedelta(days=1)).date():
                        date_str = "Ayer"
                    else:
                        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                        date_str = f"{lima_dt.day} de {meses[lima_dt.month - 1]} de {lima_dt.year}"
                except:
                    pass
            
            if date_str and date_str != last_date_str:
                burbujas += f'<div style="text-align:center; clear:both; margin: 1rem 0;"><span style="display:inline-block; background:var(--accent-bg); color:var(--text-muted); font-weight:600; font-size:0.75rem; padding:0.3rem 0.8rem; border-radius:12px; box-shadow:0 1px 2px rgba(0,0,0,0.1); border:1px solid var(--accent-border);">{date_str}</span></div>'
                last_date_str = date_str

            es_bot = m["role"] == "assistant"
            clase  = "bubble-bot" if es_bot else "bubble-user"
            lado   = "lado-der" if es_bot else "lado-izq"
            # Limpiar residuo de transcripciones antiguas inyectadas en content
            raw_content = m["content"]
            # Eliminar cualquier texto de transcripción viejo (plain text y HTML) del content
            import re as _re
            raw_content = _re.sub(r'\n+📝 Transcripción:.*', '', raw_content, flags=_re.DOTALL)
            raw_content = _re.sub(r'<br><br><b>📝 Transcripción:</b>.*', '', raw_content, flags=_re.DOTALL)
            texto  = raw_content.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            
            # Virtual group: Include visual author tag for user messages
            if not es_bot and "sender_name_override" in m:
                s_name = m.get("sender_name_override", "")
                s_waid = m.get("sender_wa_id", "")
                texto = f'<div style="background:rgba(255,255,255,0.08); padding:0.4rem 0.6rem; border-radius:4px; font-size:0.8rem; margin-bottom:0.4rem; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center;"><strong style="color:var(--text-main); font-family:var(--font-heading);">{s_name}</strong> <a href="/inbox/{s_waid}" style="color:var(--primary-color); text-decoration:none; font-weight:bold; padding:0.2rem 0.4rem; background:rgba(59, 130, 246, 0.15); border-radius:4px;">Responder ↗</a></div>' + texto
            def wrap_phone2(match):
                phone = match.group(1)
                clean_phone = __import__('re').sub(r'[\s\-]', '', phone)
                if sum(c.isdigit() for c in clean_phone) >= 7:
                    return f'<span class="chat-phone" style="text-decoration:underline; cursor:pointer; font-weight:bold;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
                return phone
            texto = __import__('re').sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone2, texto)
            
            # --- Renderizar media_id si es [sticker:ID] o [imagen:ID] ---
            import re
            
            def reemplazar_archivos_inline(match):
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
                
                caption_html = f"""<div style="font-size:0.85rem; padding:6px; max-width:350px; margin:0 auto; background:rgba(0,0,0,0.3); border-bottom-left-radius:8px; border-bottom-right-radius:8px; color:var(--text-main); word-break:break-word; border:1px solid rgba(255,255,255,0.05); border-top:none; margin-top:-5px; box-sizing:border-box;">{caption.replace('<', '&lt;').replace('>', '&gt;')}</div>""" if caption else ""
                
                if tipo == "sticker-local":
                    src_url = f"/api/media/sticker/{media_id}"
                    return f"""<div style="text-align:center;"><img src="{src_url}" style="width: 150px; height: 150px; object-fit: contain; border-radius: 8px; background: transparent; margin-bottom: 5px; display:inline-block;" alt="Sticker Local {media_id}"></div>"""
                    
                src_url = media_id if media_id.startswith("http") else f"/api/media/{media_id}"
                
                if tipo == "sticker":
                    return f"""<div style="text-align:center;"><img src="{src_url}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display:inline-block;" alt="Sticker {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/150x150?text=Sticker';"></div>"""
                elif tipo == "imagen":
                    res = f"""<div style="text-align:center; max-width: 350px; margin: 0 auto;"><img src="{src_url}" style="max-width: 100%; max-height: 350px; width: auto; object-fit: contain; border-radius: 8px; {'border-bottom-left-radius:0; border-bottom-right-radius:0;' if caption else ''} background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""
                    return res + caption_html
                elif tipo == "video":
                    res = f"""<div style="text-align:center; max-width: 350px; margin: 0 auto;"><video controls src="{src_url}" style="max-width: 100%; max-height: 350px; width: auto; object-fit: contain; border-radius: 8px; {'border-bottom-left-radius:0; border-bottom-right-radius:0;' if caption else ''} background: rgba(0,0,0,0.6); margin-bottom: 5px; display: block; margin: 0 auto;"></video></div>"""
                    return res + caption_html
                elif tipo == "audio":
                    return f"""<div class="custom-audio-player" onclick="window.toggleAudioSpeed(event, this)" style="display:flex; align-items:center; gap:0.6rem; width:100%; min-width:200px; max-width:300px; margin: 5px 0; cursor:pointer;" title="Haz clic para cambiar la velocidad">
                        <audio src="{src_url}" preload="metadata" style="display:none;" 
                            onloadedmetadata="this.parentElement.querySelector('.cap-time').textContent = window.formatAudioTime(this.duration);" 
                            ontimeupdate="this.parentElement.querySelector('.cap-progress').style.width = (this.currentTime / this.duration * 100) + '%'; this.parentElement.querySelector('.cap-time').textContent = window.formatAudioTime(this.currentTime);" 
                            onended="this.parentElement.querySelector('.icon-play').style.display='block'; this.parentElement.querySelector('.icon-pause').style.display='none'; this.currentTime=0; this.parentElement.querySelector('.cap-progress').style.width='0%'; this.parentElement.querySelector('.cap-time').textContent = window.formatAudioTime(this.duration);">
                        </audio>
                        <button class="cap-play-btn" type="button" onclick="window.toggleAudio(this)" style="background:var(--primary-color); color:white; border:none; border-radius:50%; width:38px; height:38px; display:flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0; box-shadow:0 2px 4px rgba(0,0,0,0.2); transition:transform 0.1s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                            <svg class="icon-play" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-left:2px;"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                            <svg class="icon-pause" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="display:none;"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
                        </button>
                        <div class="cap-timeline" onclick="window.seekAudio(event, this)" style="flex:1; height:6px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:4px; cursor:pointer; position:relative; overflow:hidden;">
                            <div class="cap-progress" style="width:0%; height:100%; background:var(--primary-color); position:absolute; left:0; top:0; pointer-events:none; transition: width 0.1s linear;"></div>
                        </div>
                        <span class="cap-speed" style="font-size:0.75rem; color:var(--primary-color); font-weight:700; background:rgba(255,255,255,0.7); border-radius:10px; padding:2px 6px; min-width:32px; text-align:center; transition:background 0.2s;">1x</span>
                        <span class="cap-time" style="font-size:0.75rem; color:inherit; opacity:0.8; font-weight:500; min-width:35px; text-align:right; font-family:var(--font-main);">0:00</span>
                    </div>"""
                elif tipo == "documento":
                    partes = media_id.split("|", 1)
                    doc_id = partes[0]
                    doc_name = partes[1] if len(partes) > 1 else "Documento"
                    doc_url = f"/api/media/{doc_id}"
                    return f'<div style="margin-bottom: 5px;"><a href="{doc_url}" download="{doc_name}" target="_blank" style="display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; text-decoration: none; color: inherit; font-size: 0.9rem; border: 1px solid var(--accent-border);">📎 {doc_name} <span style="font-size:0.8rem; margin-left:auto; opacity:0.6;">📥 Bajar</span></a></div>' 
                elif tipo == "vista_unica":
                    icono = "📷" if media_id == "imagen" else ("🎬" if media_id == "video" else "🎤")
                    return f'<div style="margin-bottom: 5px; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px dashed rgba(255,255,255,0.2); text-align: center; color: var(--text-dim); display:flex; flex-direction:column; align-items:center; gap:4px;"><span style="font-size: 1.2rem;">{icono} 👁️</span><span style="font-size: 0.8rem; font-weight: 500;">Archivo de Vista Única</span><span style="font-size: 0.75rem; opacity: 0.7;">(Bloqueado por privacidad de WhatsApp)</span></div>'
                return match.group(0)

            # Reemplazar todas las etiquetas multimedia incrustadas en el texto usando una función regex,
            # permitiendo que coexistan con texto (ej: "[sticker:123] | Hola")
            texto_renderizado = re.sub(r"\[(sticker-local|sticker|imagen|audio|video|documento|vista_unica):([^\]]+)\]", reemplazar_archivos_inline, texto)

            def reemplazar_ubicacion(match):
                coords_str = match.group(1)
                partes = coords_str.split(",", 2)
                lat, lon = partes[0], partes[1]
                addr = partes[2] if len(partes) > 2 else ""
                maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                addr_text = f"<br><span style='font-size:0.75rem;opacity:0.8'>📍 {addr}</span>" if addr else ""
                return f'<div style="text-align:center; margin-bottom: 4px;"><a href="{maps_url}" target="_blank" style="display:inline-block; background:rgba(255,255,255,0.05); padding:0.6rem 1rem; border-radius:12px; color:var(--text-main); text-decoration:none; border:1px solid var(--accent-border); font-size:0.85rem;">🗺️ <span style="text-decoration:underline;">Ver Ubicación de WhatsApp en Google Maps</span>{addr_text}</a></div>'

            texto_renderizado = re.sub(r"\[ubicacion:([^\]]+)\]", reemplazar_ubicacion, texto_renderizado)
            
            # Limpiar posibles delimitadores huérfanos si quedó un texto como "<HTML> | PN" 
            texto_renderizado = texto_renderizado.replace("</div> | ", "</div><br>")
            
            if texto.startswith('[sticker') and texto.endswith(']'):
                clase += " bubble-sticker"
                
            # Formatear el indicador de respuesta nativa
            import re
            match = re.match(r"^\[\[REPLY\|(.*?)\]\](.*)$", texto_renderizado, flags=re.DOTALL)
            if match:
                texto_citado = match.group(1)
                texto_restante = match.group(2)
                html_reply = f'<div style="font-size:0.75rem; color:var(--text-muted); background:rgba(0,0,0,0.15); padding:0.35rem 0.6rem; border-radius:6px; margin-bottom:0.4rem; border-left:3px solid var(--primary-color); display:flex; flex-direction:column; max-width:100%; overflow:hidden;"><span style="font-weight:600;font-size:0.65rem;margin-bottom:0.1rem;opacity:0.8;">Respondió a:</span><span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{texto_citado}</span></div>'
                texto_renderizado = html_reply + texto_restante
                
            # Formatear la vista de plantillas salientes
            match_tpl = re.match(r"^\[Plantilla enviada:\s*(.*?)\]$", texto_renderizado, flags=re.DOTALL)
            if match_tpl:
                tpl_content = match_tpl.group(1).strip()
                # Split title from the rest if available
                parts = tpl_content.split("<br>", 1)
                tpl_title = parts[0]
                tpl_body = f'<div style="margin-top:0.6rem; padding-top:0.6rem; border-top:1px solid rgba(16,185,129,0.2); font-size:0.85rem; color:var(--text-main); line-height:1.4;">{parts[1]}</div>' if len(parts) > 1 else ""
                
                texto_renderizado = f'<div style="background:rgba(255,255,255,0.05); border-left:3px solid #10b981; padding:0.6rem; border-radius:6px; margin:-0.2rem;"><div style="font-size:0.7rem; color:#10b981; font-weight:600; text-transform:uppercase; margin-bottom:0.4rem; display:flex; align-items:center; gap:0.3rem;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> PLANTILLA META: {tpl_title}</div>{tpl_body}</div>'
                
            def linkify_text(match):
                if match.group(1): return match.group(1)
                url = match.group(2)
                # Cleanup common trailing punctuation that users might type right after the URL
                trailing = ""
                while url and url[-1] in ".,!?)":
                    trailing = url[-1] + trailing
                    url = url[:-1]
                
                href = url if url.startswith('http') else 'http://' + url
                return f'<a href="{href}" target="_blank" rel="noopener noreferrer" style="text-decoration:underline; font-weight:500; color:inherit;">{url}</a>{trailing}'
                
            texto_renderizado = re.sub(r'(<[^>]+>)|((?:https?://|www\.|wa\.me/)[^\s<>]+|[a-zA-Z0-9_-]+\.[a-zA-Z]{2,5}(?:/[^\s<>]*)?)', linkify_text, texto_renderizado)
            
            wamid = m.get("msg_id", "")
            wamid_attr = f' id="msg-{wamid}" data-wamid="{wamid}"' if wamid else ""
            
            meta_html = ""
            ts_html = ""
            status_html = ""

            if "timestamp" in m:
                try:
                    ts_val = int(m["timestamp"])
                    if ts_val > 1e11: ts_val //= 1000
                    utc_dt = datetime.utcfromtimestamp(ts_val)
                    lima_dt = utc_dt - timedelta(hours=5)
                    ts_str = lima_dt.strftime("%H:%M")
                    ts_html = f'<span class="msg-ts">{ts_str}</span>'
                except:
                    pass

            # Show tick only for assistant
            if es_bot and "status" in m:
                st = m["status"]
                if st == "sent":
                    tick = "✓"
                    color = "rgba(255,255,255,0.7)"
                elif st == "delivered":
                    tick = "✓✓"
                    color = "rgba(255,255,255,0.7)"
                elif st == "read":
                    tick = "✓✓"
                    color = "#34b7f1" 
                else:
                    tick = "✓"
                    color = "rgba(255,255,255,0.7)"
                status_html = f'<span class="msg-status" style="color:{color}; font-size:0.75rem; margin-left:4px; font-weight: bold;">{tick}</span>'

            if ts_html or status_html:
                transcribe_btn_html = ""
                import re
                if "[audio:" in texto:
                    m_audio = re.search(r"\[audio:([^\]]+)\]", m.get("content", ""))
                    if m_audio:
                        media_id = m_audio.group(1)
                        transcribe_btn_html = f'<button type="button" class="btn-transcribe" onclick="window.transcribeAudio(event, this, \'{media_id}\', \'{wa_id}\', \'{wamid}\')" style="background:transparent; border:none; color:var(--text-main); font-size:0.65rem; cursor:pointer; font-weight:600; padding:0; margin-right:auto; text-decoration:underline;">Transcribir</button>'
                
                meta_html = f'<div class="msg-meta" style="text-align:right; margin-top:4px; font-size:0.65rem; color:inherit; opacity:0.8; display:flex; justify-content:flex-end; align-items:center; gap:6px;">{transcribe_btn_html}{ts_html}{status_html}</div>'

            # Extraer datos para el panel de info
            sent_by_val = m.get("sent_by", "")
            ts_unix = m.get("timestamp", "")
            delivered_ts = m.get("delivered_ts", "")
            read_ts = m.get("read_ts", "")
            msg_status = m.get("status", "")
            
            extra_data = ""
            if es_bot:
                qr_title_val = m.get("quick_reply_title", "")
                extra_data = f' data-sent-by="{sent_by_val}" data-ts="{ts_unix}" data-delivered-ts="{delivered_ts}" data-read-ts="{read_ts}" data-status="{msg_status}" data-quick-reply="{qr_title_val}"'
            
            is_starred = m.get("is_starred", False)
            is_pinned = m.get("is_pinned", False)
            extra_data += f' data-starred="{str(is_starred).lower()}" data-pinned="{str(is_pinned).lower()}"'
            
            if is_starred:
                meta_html += '<span style="color:#fbbf24; margin-left:4px; font-size:12px;">★</span>'
                starred_messages.append(m)
            if is_pinned:
                pinned_messages.append(m)
            
            transcrip_html = ""
            if m.get("transcripcion"):
                transcrip_html = f'<div style="margin-top:0.5rem; padding-top:0.4rem; border-top:1px dashed rgba(255,255,255,0.15); font-size:0.8rem; font-style:italic; line-height:1.3; color:inherit; opacity:0.9;">📝 {m.get("transcripcion")}</div>'
            
            burbujas += f'<div class="bubble {clase} {lado}"{wamid_attr}{extra_data} title="Click derecho (PC) o mantener presionado (M\u00f3vil) para opciones">{texto_renderizado}{transcrip_html}{meta_html}</div>'

            
        if not burbujas:
            burbujas = '<div style="text-align:center;opacity:0.5;margin-top:2rem">Conversación iniciada...</div>'

        # Cabecera superior del chat
        status_bar = ""
        if not activo_chat:
            status_bar = f"""
            <div style="background:var(--danger-color);color:white;padding:0.5rem 1rem;font-size:0.85rem;font-weight:600;display:flex;justify-content:space-between;align-items:center;">
                Atención manual en curso
                <form method="post" action="/admin/reactivar/{wa_id}" style="margin:0">
                  <input type="hidden" name="redirect" value="/inbox/{wa_id}?tab={tab}">
                  <button type="submit" style="background:white;color:var(--danger-color);border:none;padding:0.3rem 0.8rem;border-radius:6px;font-weight:700;cursor:pointer;transition:transform 0.2s;">[OK] Reactivar Bot</button>
                </form>
            </div>"""
        else:
            status_bar = f"""
            <div style="background:var(--success-color);color:white;padding:0.5rem 1rem;font-size:0.85rem;font-weight:600;display:flex;justify-content:space-between;align-items:center;">
                Bot IA respondiendo automáticamente
                <form method="post" action="/api/admin/pausar/{wa_id}" style="margin:0">
                  <input type="hidden" name="redirect" value="/inbox/{wa_id}?tab={tab}">
                  <button type="submit" style="background:white;color:var(--success-color);border:none;padding:0.3rem 0.8rem;border-radius:6px;font-weight:700;cursor:pointer;transition:transform 0.2s;">⏸️ Pausar IA</button>
                </form>
            </div>"""

        chat_box = ""
        if s_fake_vg:
            chat_box = """<div style="padding:0.75rem; color:#c084fc; text-align:center; font-size:0.85rem; font-weight:600; display:flex; align-items:center; justify-content:center; gap:0.5rem;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg> GRUPO VIRTUAL DE SOLO LECTURA. HAGA CLIC EN EL LOGO DE UN MENSAJE PARA ABRIR SU CHAT PRIVADO.</div>"""
        elif activo_chat:
            chat_box = """
            <div id="qrProgressContainer" style="display:none; align-items:center; background:var(--accent-bg); padding:0.5rem 1rem; margin-bottom:0.5rem; border-radius:8px; gap:0.5rem; font-size:0.8rem; flex-direction:column; border:1px solid var(--accent-border);">
                <div style="width:100%; display:flex; justify-content:space-between; color:var(--text-main); font-weight:600;"><span id="qrProgressText">Procesando...</span></div>
                <div style="width:100%; height:6px; background:var(--bg-main); border-radius:4px; overflow:hidden;"><div id="qrProgressFill" style="height:100%; width:0%; background:var(--primary-color); transition:width 0.3s;"></div></div>
            </div>
            <div style="opacity:0.6;font-size:0.85rem;color:var(--text-muted);display:flex;align-items:center;justify-content:center;padding:0.5rem;">
                El Bot IA está controlando este chat. Pausa al bot para intervenir.
            </div>"""
        else:
            chat_box = f"""
            <div id="qrProgressContainer" style="display:none; align-items:center; background:var(--accent-bg); padding:0.5rem 1rem; margin-bottom:0.5rem; border-radius:8px; gap:0.5rem; font-size:0.8rem; flex-direction:column; border:1px solid var(--accent-border);">
                <div style="width:100%; display:flex; justify-content:space-between; color:var(--text-main); font-weight:600;"><span id="qrProgressText">Procesando...</span></div>
                <div style="width:100%; height:6px; background:var(--bg-main); border-radius:4px; overflow:hidden;"><div id="qrProgressFill" style="height:100%; width:0%; background:var(--primary-color); transition:width 0.3s;"></div></div>
            </div>
            <div id="replyPreviewContainer" style="display:none; align-items:center; justify-content:space-between; background:var(--accent-bg); padding: 0.5rem 1rem; border-left: 3px solid var(--primary-color); font-size: 0.85rem; color: var(--text-muted); border-radius: 8px 8px 0 0; margin-bottom: -0.5rem; position: relative;">
                <span style="font-family:var(--font-main);">Respondiendo a: <span id="replyPreviewTxt" style="color:var(--text-main);font-weight:600;">...</span></span>
                <button type="button" onclick="document.getElementById('replyPreviewContainer').style.display='none'; document.getElementById('replyToWamid').value='';" style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:1.1rem;padding:0;">×</button>
            </div>
            
            <form onsubmit="window.enviarMensajeManual(event, '{wa_id}'); return false;" style="display:flex; gap:0.4rem; width:100%; margin:0; position:relative; align-items:flex-end; box-sizing:border-box; max-width:100%;">
                <input type="hidden" id="replyToWamid" value="">

                <!-- Popover combinado flotando sobre todo -->
                <div id="combinedEmojiMenu" style="display:none; position:absolute; bottom:calc(100% + 0.5rem); left:0; width:320px; height:380px; max-width:90vw; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:16px; box-shadow:0 8px 16px rgba(0,0,0,0.5); z-index:100; flex-direction:column; overflow:hidden;">
                    <!-- Tab Headers -->
                    <div style="display:flex; border-bottom:1px solid var(--accent-border); background:var(--accent-bg);">
                        <button type="button" id="btnTabEmoji" onclick="document.getElementById('tabEmoji').style.display='flex'; document.getElementById('tabSticker').style.display='none'; this.style.borderBottom='2px solid var(--primary-color)'; this.style.opacity='1'; document.getElementById('btnTabSticker').style.borderBottom='2px solid transparent'; document.getElementById('btnTabSticker').style.opacity='0.6';" style="flex:1; padding:0.8rem; background:transparent; border:none; cursor:pointer; color:var(--text-main); font-weight:600; border-bottom:2px solid var(--primary-color); outline:none;">Emojis</button>
                        <button type="button" id="btnTabSticker" onclick="document.getElementById('tabSticker').style.display='flex'; document.getElementById('tabEmoji').style.display='none'; this.style.borderBottom='2px solid var(--primary-color)'; this.style.opacity='1'; document.getElementById('btnTabEmoji').style.borderBottom='2px solid transparent'; document.getElementById('btnTabEmoji').style.opacity='0.6';" style="flex:1; padding:0.8rem; background:transparent; border:none; cursor:pointer; color:var(--text-main); font-weight:600; border-bottom:2px solid transparent; opacity:0.6; outline:none;">Stickers</button>
                    </div>
                    <!-- Tab Contents -->
                    <div style="flex:1; display:flex; flex-direction:column; overflow:hidden;">
                        <!-- Emoji Tab -->
                        <div id="tabEmoji" style="flex:1; display:flex; flex-direction:column; overflow:hidden;">
                            <emoji-picker style="width:100%; height:100%; --background: var(--bg-main); --border-color: transparent;"></emoji-picker>
                        </div>
                        <!-- Sticker Tab -->
                        <div id="tabSticker" style="flex:1; display:none; flex-direction:column; overflow-y:auto; padding:0.5rem; background:var(--bg-sidebar);">
                            <div id="stickersGrid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(70px, 1fr)); gap:5px; padding-bottom:1rem;">
                                <div style="grid-column:1/-1; text-align:center; padding:1rem; opacity:0.5; color:var(--text-muted); font-size:0.85rem;">Cargando...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- CENTRO: Input Píldora que abarca todo lo central -->
                <div style="flex:1; display:flex; align-items:flex-end; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:24px; padding:0.2rem 0.4rem; position:relative; min-height:46px; min-width:0; box-sizing:border-box;">
                    
                    <!-- attach menu -->
                    <div id="attachMenu" style="display:none; position:absolute; bottom:calc(100% + 0.8rem); right:10px; width:190px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.5); padding:0.5rem; flex-direction:column; gap:0.2rem; z-index:100;">
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').removeAttribute('capture'); document.getElementById('hiddenFileInput').setAttribute('data-mode', 'imagen'); document.getElementById('hiddenFileInput').accept='image/*'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg> Subir Imagen
                        </button>
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'video'); document.getElementById('hiddenFileInput').accept='video/*'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg> Subir Video
                        </button>
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'audio'); document.getElementById('hiddenFileInput').accept='audio/*'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg> Subir Audio
                        </button>
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'documento'); document.getElementById('hiddenFileInput').accept='.pdf,.doc,.docx,.xls,.xlsx,.txt'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Subir Documento
                        </button>
                    </div>

                    <!-- Emoji Button Inside -->
                    <button type="button" onclick="const m = document.getElementById('combinedEmojiMenu'); m.style.display = m.style.display==='none'?'flex':'none'; if(m.style.display==='flex') {{ document.getElementById('btnTabEmoji').click(); if(window.cargarStickers) window.cargarStickers(); }}" style="background:transparent; border:none; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s; flex-shrink:0; margin-bottom: 2px;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Emojis y Stickers">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
                    </button>

                    <textarea id="manualMsgInput" placeholder="Mensaje..." style="flex:1; min-width:0; width:100%; height:42px; min-height:42px; max-height:160px; background:transparent; border:none; outline:none; color:var(--text-main); font-size:1rem; padding:10px 0.2rem; font-family:var(--font-main); box-sizing:border-box; resize:none; overflow-y:hidden; line-height:22px; transition: height 0.1s ease-out;" autocomplete="off" oninput="if(window.checkQuickReplyTrigger) window.checkQuickReplyTrigger(this); if(window.toggleSendMicButton) window.toggleSendMicButton(); if(window.autoResizeInput) window.autoResizeInput();" onkeydown="if(event.key === 'Enter' && !event.shiftKey) {{ event.preventDefault(); window.enviarMensajeManual(event, '{wa_id}'); }}"></textarea>
                    
                    <!-- Right utilities inside -->
                    <div style="display:flex; flex-shrink:0; align-items:center; margin-bottom: 3px;">
                        <!-- Respuestas Rápidas & Plantillas -->
                        <button type="button" id="btnRightQR" onclick="const side = document.getElementById('rightSidebar'); if(side.style.display==='none' || !side.style.display){{ side.style.display='flex'; if(window.cargarQuickReplies) window.cargarQuickReplies(); if(window.cargarPlantillas) window.cargarPlantillas(); setTimeout(()=>document.getElementById('qrSearchFilter').focus(), 50); }} else {{ side.style.display='none'; }}" style="background:transparent; border:none; width:32px; height:32px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Respuestas Rápidas y Plantillas">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                        </button>
                        <!-- Clip -->
                        <button type="button" id="btnRightClip" onclick="const m = document.getElementById('attachMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:transparent; border:none; width:32px; height:32px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Adjuntar">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transform: rotate(45deg);"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                        </button>
                        <!-- Camera Mode Selector Menu -->
                        <div id="cameraMenu" style="display:none; position:absolute; bottom:calc(100% + 0.8rem); right:40px; width:160px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.5); padding:0.5rem; flex-direction:column; gap:0.2rem; z-index:100;">
                            <button type="button" onclick="document.getElementById('cameraMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'media'); document.getElementById('hiddenFileInput').accept='image/*'; document.getElementById('hiddenFileInput').setAttribute('capture', 'environment'); document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                                📷 Tomar Foto
                            </button>
                            <button type="button" onclick="document.getElementById('cameraMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'media'); document.getElementById('hiddenFileInput').accept='video/*'; document.getElementById('hiddenFileInput').setAttribute('capture', 'environment'); document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                                🎬 Grabar Video
                            </button>
                        </div>
                        
                        <!-- Cámara (Selector) -->
                        <button type="button" id="btnRightPhoto" onclick="const cm = document.getElementById('cameraMenu'); cm.style.display = cm.style.display==='none'?'flex':'none';" style="background:transparent; border:none; width:32px; height:32px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Cámara (Foto y Video)">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                        </button>
                        
                        <!-- Micrófono o Enviar -->
                        <!-- Send Button (Toggle) -->
                        <button type="submit" id="btnSubmitForm" style="background:transparent;color:var(--text-muted);border:none;width:32px;height:32px;display:none;align-items:center;justify-content:center;cursor:pointer;transition:color 0.2s; flex-shrink:0;" onmouseover="this.style.color='var(--primary-color)'" onmouseout="this.style.color='var(--text-muted)'" title="Enviar">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none" style="margin-left: 2px;"><line x1="22" y1="2" x2="11" y2="13" stroke="currentColor" stroke-width="2"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                        </button>
                        <!-- Record Audio Button (Toggle) -->
                        <button type="button" id="btnRecordAudio" style="background:transparent;color:var(--text-muted);border:none;width:32px;height:32px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:color 0.2s; flex-shrink:0;" onmouseover="this.style.color='var(--primary-color)'" onmouseout="this.style.color='var(--text-muted)'" title="Grabar nota de voz">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
                        </button>
                        <!-- Cancel Audio -->
                        <button type="button" id="btnCancelAudio" style="background:transparent; color:var(--danger-color); border:none; width:32px; height:32px; display:none; align-items:center; justify-content:center; cursor:pointer; transition:transform 0.2s; flex-shrink:0;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'" title="Cancelar grabación">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                        </button>
                    </div>
                </div>
            </form>            """

        session_tags = s.get("etiquetas", [])
        if session_tags is None: session_tags = []
        tags_bar = ""
        for tid in session_tags:
            lbl = next((l for l in global_labels if l.get("id") == tid), None)
            if lbl:
                col = lbl.get("color", "#94a3b8")
                nm = lbl.get("name", "Etiqueta")
                tags_bar += f'<span style="background:{col}22; color:{col}; font-size:0.65rem; padding:0.15rem 0.4rem; border-radius:4px; font-weight:600; border: 1px solid {col}44;">{nm}</span>'

        pinned_html = ""
        if pinned_messages:
            last_pinned = pinned_messages[-1]
            p_content = last_pinned.get("content", "Mensaje multimedia").replace('\n', ' ').replace("<", "&lt;").replace(">", "&gt;")
            if len(p_content) > 200: p_content = p_content[:200] + "..."
            p_wamid = last_pinned.get("msg_id", "")
            pinned_html = f'''
            <div style="background:var(--accent-bg); color:var(--text-main); padding:8px 12px; border-bottom:1px solid var(--accent-border); display:flex; align-items:center; gap:8px; cursor:pointer; font-size:0.85rem;" onclick="document.getElementById('msg-{p_wamid}')?.scrollIntoView({{behavior: 'smooth', block: 'center'}})">
                <span style="color:#fbbf24; font-size:16px;">📌</span>
                <div style="flex:1; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;">{p_content}</div>
            </div>
            '''

        starred_items_html = ""
        for st in reversed(starred_messages):
            s_content = st.get("content", "Mensaje multimedia").replace('\n', ' ').replace("<", "&lt;").replace(">", "&gt;")
            if len(s_content) > 300: s_content = s_content[:300] + "..."
            s_wamid = st.get("msg_id", "")
            
            # Formatear la hora
            s_date_str = ""
            if st.get("timestamp"):
                try:
                    ts_val = int(st.get("timestamp"))
                    if ts_val > 1e11: ts_val //= 1000
                    s_dt = datetime.utcfromtimestamp(ts_val) - timedelta(hours=5)
                    s_date_str = s_dt.strftime("%d/%m/%Y %H:%M")
                except:
                    pass

            starred_items_html += f'''
            <div style="background:var(--bg-main); padding:10px; border-radius:6px; margin-bottom:8px; border:1px solid var(--accent-border); cursor:pointer; font-size:0.85rem; transition: background 0.2s;" onmouseover="this.style.background='var(--primary-color)'; this.style.color='white'" onmouseout="this.style.background='var(--bg-main)'; this.style.color='inherit'" onclick="document.getElementById('msg-{s_wamid}')?.scrollIntoView({{behavior: 'smooth', block: 'center'}}); document.getElementById('modalDestacados').style.display='none';">
                <div style="opacity:0.7; font-size:0.75rem; margin-bottom:4px; display:flex; justify-content:space-between;">
                    <span>{st.get("role", "user").capitalize()}</span>
                    <span>{s_date_str}</span>
                </div>
                <div>{s_content}</div>
            </div>
            '''
        if not starred_items_html:
            starred_items_html = "<div style='text-align:center; color:var(--text-muted); font-size:0.85rem; padding:2rem 0;'>No hay mensajes destacados en esta conversación.</div>"
            
        starred_modal_html = f'''
        <div id="modalDestacados" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.6); z-index:99999; align-items:center; justify-content:center; backdrop-filter:blur(2px);">
            <div style="background:var(--accent-bg); width:90%; max-width:400px; max-height:80vh; border-radius:12px; display:flex; flex-direction:column; box-shadow:0 10px 25px rgba(0,0,0,0.5); overflow:hidden;">
                <div style="padding:15px; border-bottom:1px solid var(--accent-border); display:flex; justify-content:space-between; align-items:center; background:var(--bg-main);">
                    <h3 style="margin:0; font-size:1.1rem; display:flex; align-items:center; gap:8px;"><span style="color:#fbbf24;">⭐️</span> Mensajes Destacados</h3>
                    <button onclick="document.getElementById('modalDestacados').style.display='none'" style="background:none; border:none; color:var(--text-muted); font-size:1.5rem; cursor:pointer; padding:0; line-height:1;">&times;</button>
                </div>
                <div class="hide-scrollbar" style="padding:15px; overflow-y:auto; flex:1; background:var(--accent-bg);">
                    {starred_items_html}
                </div>
            </div>
        </div>
        '''

        chat_viewer_html = f"""
        <div style="display:flex; flex-direction:row; height:100%; width:100%;">
            <!-- START CHAT MAIN COLUMN -->
            <div style="flex:1; display:flex; flex-direction:column; min-width:0; background:transparent;">
                {status_bar}
                {pinned_html}
            <div style="padding:1.5rem;border-bottom:1px solid var(--accent-border);display:flex;align-items:center;background:var(--bg-main);">
                    <a href="/inbox?tab={tab}" class="btn-responsive-back" title="Volver a la lista">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                    </a>
                    <div style="width:40px;height:40px;border-radius:50%;background:var(--primary-color);color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;margin-right:1rem;font-size:1.2rem;flex-shrink:0">{nombre_chat[0].upper()}</div>
                    <div style="min-width:0; flex:1;">
                        <h3 style="margin:0;font-size:1.1rem;font-family:var(--font-heading);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:0.5rem;cursor:context-menu;" title="Click derecho para ver mensajes destacados" oncontextmenu="document.getElementById('modalDestacados').style.display='flex'; return false;">
                            {nombre_chat} {tags_bar}
                        </h3>
                        <small style="color:var(--text-muted)">+{wa_id}</small>
                    </div>

                    <!-- Botón Ver Pedido ERP -->
                    <button type="button" onclick="abrirModalPedido('{wa_id}')" style="background:linear-gradient(135deg, var(--primary-color), #059669); color:white; border:none; padding:0.4rem 0.8rem; border-radius:8px; font-size:0.85rem; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:0.4rem; margin-right:0.5rem; box-shadow:0 2px 4px rgba(0,0,0,0.1); transition:transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.15)';" onmouseout="this.style.transform='none'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)';">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
                        Ver Pedido
                    </button>

                    <!-- Botón de gestionar etiquetas -->
                    <div style="position:relative;">
                        <button type="button" onclick="const m = document.getElementById('chatLabelMenu'); m.style.display = m.style.display==='none'?'flex':'none'; if(m.style.display==='flex') cargarChatLabels();" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem; padding:0.5rem; border-radius:50%; transition:background 0.2s;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='none'" title="Etiquetas del Chat">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                        </button>
                        <div id="chatLabelMenu" style="display:none; position:absolute; top:calc(100% + 0.5rem); right:0; width:220px; background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.5); padding:0.5rem; flex-direction:column; gap:0.4rem; z-index:100;">
                            <div style="font-weight:600; font-size:0.8rem; color:var(--text-muted); padding:0.3rem 0.5rem; border-bottom:1px solid var(--accent-border); display:flex; justify-content:space-between; align-items:center;">
                                Etiquetas 
                                {f'<button type="button" onclick="crearGlobalLabel()" style="background:none; border:none; color:var(--primary-color); cursor:pointer; font-size:1rem; padding:0;" title="Nueva Etiqueta Global">+</button>' if es_admin(request) else ''}
                            </div>
                            <div id="chatLabelList" style="display:flex; flex-direction:column; gap:0.2rem; max-height:220px; overflow-y:auto;">
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="flex:1;overflow-y:auto;padding:1.5rem 1.5rem 0.5rem 1.5rem;display:flex;flex-direction:column;gap:0.5rem;" id="chatScroll">
                    {burbujas}
                </div>
                
                <div style="padding:0.2rem 1rem 1rem 1rem; background:transparent; width:100%; max-width:100vw; box-sizing:border-box;">
                    {chat_box}
                </div>
                {starred_modal_html}
            </div>
            <!-- END CHAT MAIN COLUMN -->

            <!-- START RIGHT SIDEBAR (CRM Tools) -->
            <div id="rightSidebar" class="hide-scrollbar" style="width:340px; border-left:1px solid var(--accent-border); background:var(--accent-bg); display:none; flex-direction:column; position:relative; box-shadow:-4px 0 15px rgba(0,0,0,0.1);">
            <div style="padding:1.5rem; border-bottom:1px solid var(--accent-border); display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="font-family:var(--font-heading); font-size:1.1rem; flex:1; color:var(--text-main); margin:0;"> Respuestas Rápidas</h3>
                    <button onclick="document.getElementById('rightSidebar').style.display='none'" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem;">×</button>
                </div>
                <div style="padding:1rem 1.5rem; border-bottom:1px solid var(--accent-border); background:var(--bg-main);">
                    <div style="display:flex; gap:0.5rem; justify-content:space-between;">
                        <input type="text" id="qrSearchFilter" placeholder="Buscar... (/)" onkeyup="filtrarQuickReplies(this.value)" style="flex:1; padding:0.6rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.85rem;">
                        <button onclick="abrirModalCrearQR()" style="background:var(--primary-color); color:white; border:none; border-radius:6px; padding:0 0.8rem; cursor:pointer;" title="Crear nueva respuesta rápida">NUEVA</button>
                    </div>
                </div>
                <div id="quickRepliesList" style="flex:1; overflow-y:auto; padding:1.5rem; display:flex; flex-direction:column; gap:0.6rem;">
                    <div style="font-size:0.8rem; color:var(--text-muted); text-align:center;">Cargando...</div>
                </div>

                <!-- Plantillas Subsection -->
                <div style="padding:1rem 1.5rem; border-top:1px solid var(--accent-border); background:var(--accent-bg); display:flex; flex-direction:column; max-height:220px; flex-shrink:0;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
                        <h4 style="margin:0; font-size:0.85rem; color:var(--text-main); font-weight:600;">Plantillas (Meta)</h4>
                        <button onclick="if(window.crearPlantilla) window.crearPlantilla()" style="background:var(--primary-color); color:white; border:none; border-radius:4px; padding:0.2rem 0.6rem; font-size:0.75rem; cursor:pointer; font-weight:bold;" title="Añadir Plantilla">AÑADIR</button>
                    </div>
                    <div id="templateList" class="hide-scrollbar" style="overflow-y:auto; display:flex; flex-direction:column; gap:0.4rem; flex:1;">
                        <div style="font-size:0.8rem; color:var(--text-muted); text-align:center;">Cargando plantillas...</div>
                    </div>
                </div>

                <!-- Hidden section / Sub-panel for Creating QR -->
                <div id="qrCreateModal" style="display:none; position:absolute; inset:0; background:var(--bg-main); flex-direction:column; z-index:10; border-left:1px solid var(--accent-border);">
                    <div style="padding:1.2rem 1.5rem; border-bottom:1px solid var(--accent-border); display:flex; justify-content:space-between; align-items:center; background:var(--accent-bg);">
                        <h3 id="modalTitleText" style="font-family:var(--font-heading); font-size:1.05rem; flex:1; margin:0;">Crear Respuesta</h3>
                        <input type="hidden" id="newQrId" value="">
                        <button onclick="document.getElementById('qrCreateModal').style.display='none'" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem;">×</button>
                    </div>
                    <div style="padding:1.2rem 1.5rem; display:flex; flex-direction:column; gap:1rem; flex:1; overflow-y:auto;">
                        <div style="display:flex; gap:0.8rem;">
                            <div style="flex:2;">
                                <label style="display:block; font-size:0.8rem; color:var(--text-muted); margin-bottom:0.4rem; font-weight:600;">Atajo / Título</label>
                                <input type="text" id="newQrTitle" placeholder="ej: saludo" style="width:100%; padding:0.55rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.85rem; box-sizing:border-box;">
                            </div>
                            <div style="flex:1;">
                                <label style="display:block; font-size:0.8rem; color:var(--text-muted); margin-bottom:0.4rem; font-weight:600;">Espera (ms)</label>
                                <input type="number" id="newQrDelay" placeholder="1500" value="1500" style="width:100%; padding:0.55rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.85rem; box-sizing:border-box;">
                            </div>
                        </div>
                        <div>
                            <div style="display:flex; flex-direction:column; gap:0.5rem; margin-bottom:0.5rem;">
                                <label style="font-size:0.8rem; color:var(--text-muted); font-weight:600;">Mensajes (Secuencia)</label>
                                <div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
                                    <button onclick="addQrMessageField('text')" style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); color:var(--success-color); font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">+ Texto</button>
                                    <button onclick="addQrMessageField('image')" style="background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); color:var(--primary-color); font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🖼 Img</button>
                                    <button onclick="addQrMessageField('video')" style="background:rgba(139,92,246,0.15); border:1px solid rgba(139,92,246,0.3); color:#a78bfa; font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🎬 Vid</button>
                                    <button onclick="addQrMessageField('audio')" style="background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.3); color:#fbbf24; font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🎵 Audio</button>
                                    <button onclick="addQrMessageField('action_label')" style="background:rgba(236,72,153,0.15); border:1px solid rgba(236,72,153,0.3); color:#ec4899; font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🏷 Acción Tag</button>
                                </div>
                            </div>
                            <div id="qrMessagesContainer" style="display:flex; flex-direction:column; gap:0.6rem;"></div>
                            <button onclick="insertarVariableQR('#nombre')" style="margin-top:0.5rem; background:rgba(59,130,246,0.1); border:1px dashed rgba(59,130,246,0.4); color:var(--primary-color); font-size:0.75rem; padding:0.3rem 0.8rem; border-radius:5px; cursor:pointer;">+ insertar #nombre</button>
                        </div>
                        <div>
                            <label style="display:block; font-size:0.8rem; color:var(--text-muted); margin-bottom:0.4rem; font-weight:600;">Categoría</label>
                            <input type="text" id="newQrCat" placeholder="General" style="width:100%; padding:0.55rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.85rem; box-sizing:border-box;">
                        </div>
                        <div>
                            <label style="display:block; font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem; font-weight:600;">Etiquetas</label>
                            <div id="qrLabelPicker" style="display:flex; flex-wrap:wrap; gap:0.4rem; min-height:32px; padding:0.4rem; background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:6px;">
                                <span style="font-size:0.75rem; color:var(--text-muted); align-self:center;" id="qrLabelPickerEmpty">Sin etiquetas seleccionadas</span>
                            </div>
                            <div id="qrLabelOptions" style="display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.4rem;"></div>
                        </div>
                    </div>
                    <div style="padding:1rem 1.5rem; border-top:1px solid var(--accent-border);">
                        <button onclick="guardarNuevoQR()" style="width:100%; background:var(--primary-color); color:white; border:none; padding:0.75rem; border-radius:6px; font-weight:600; cursor:pointer; font-size:0.9rem;">Guardar Respuesta</button>
                    </div>
                </div>
            </div>
            <!-- END RIGHT SIDEBAR -->
        </div>
        <script>
            window.isSendingSequence = false; window.isSendingSequence = false;
            let isSendingSequence = false; window.isSendingSequence = false;
            
            async function aplicarQuickReply(qrId) {{
                if(isSendingSequence) return alert("Hay una secuencia enviándose, por favor espera.");
                
                const qr = quickRepliesCache.find(q => q.id === qrId);
                if(!qr) return;
                
                // Support both old string[] and new object[] formats
                let msgs = (qr.mensajes && qr.mensajes.length > 0) ? qr.mensajes : [{{type:'text', content: qr.content}}];
                let delay = isNaN(parseInt(qr.delay_ms)) ? 1500 : parseInt(qr.delay_ms);
                
                let nombreCliente = "{nombre_chat}";
                const input = document.getElementById("manualMsgInput");
                if(!input) return;
                
                document.getElementById('rightSidebar').style.display = 'none';
                
                const form = input.closest('form');
                const btn = form.querySelector('button[type="submit"]');
                
                const progressBarContainer = document.getElementById('qrProgressContainer');
                const progressBarFill = document.getElementById('qrProgressFill');
                const progressText = document.getElementById('qrProgressText');
                
                if(progressBarContainer) progressBarContainer.style.display = 'flex';
                isSendingSequence = true; window.isSendingSequence = true;
                
                for (let i = 0; i < msgs.length; i++) {{
                    const msgObj = typeof msgs[i] === 'string' ? {{type:'text', content: msgs[i]}} : msgs[i];
                    const msgType = msgObj.type || 'text';
                    
                    if(progressBarFill) {{
                        const pct = ((i) / msgs.length) * 100;
                        progressBarFill.style.width = pct + "%";
                        const typeLabel = msgType === 'text' ? '📝' : msgType === 'image' ? '🖼' : msgType === 'video' ? '🎬' : '🎵';
                        progressText.innerText = `${{typeLabel}} Enviando ${{i+1}}/${{msgs.length}}...`;
                    }}
                    
                    // Compose the tag/text to put in input
                    if(msgType === 'action_label') {{
                        if (msgObj.media_id) {{
                            try {{
                                await fetch("/api/admin/chats/labels/toggle", {{
                                    method: "POST",
                                    headers: {{"Content-Type":"application/json"}},
                                    body: JSON.stringify({{ wa_id: "{wa_id}", label_id: msgObj.media_id, action: "toggle" }})
                                }});
                            }} catch(e) {{}}
                        }}
                        if (i < msgs.length - 1) await new Promise(r => setTimeout(r, delay / 2));
                        continue;
                    }}

                    let finalMsg;
                    if(msgType === 'text') {{
                        finalMsg = (msgObj.content || '').replace(/#nombre/gi, nombreCliente);
                    }} else if(msgType === 'image') {{
                        finalMsg = `[imagen:${{msgObj.media_id}}]`;
                    }} else if(msgType === 'video') {{
                        finalMsg = `[video:${{msgObj.media_id}}]`;
                    }} else if(msgType === 'audio') {{
                        finalMsg = `[audio:${{msgObj.media_id}}]`;
                    }} else {{
                        finalMsg = msgObj.content || '';
                    }}
                    
                    if(!finalMsg) {{ i < msgs.length-1 && await new Promise(r=>setTimeout(r, delay)); continue; }}
                    
                    if (window.enviarMensajeDirecto) {{
                        await window.enviarMensajeDirecto("{wa_id}", finalMsg, qr.title);
                    }} else {{
                        const endsWithSlash = input.value.trimEnd().endsWith("/");
                        window._nextQuickReplyTitle = qr.title;
                        input.value = (endsWithSlash && i===0) ? input.value.trimEnd().slice(0,-1) + finalMsg : finalMsg;
                        if(btn) btn.click();
                    }}
                    
                    if (i < msgs.length - 1) {{
                        await new Promise(r => setTimeout(r, delay));
                    }}
                }}
                
                if(progressBarFill) {{
                    progressBarFill.style.width = "100%";
                    progressText.innerText = `[OK] Secuencia enviada (${{msgs.length}} mensaje${{msgs.length>1?'s':''}})`;
                    setTimeout(() => {{
                        progressBarContainer.style.display = 'none';
                    }}, 2500);
                }}
                
                isSendingSequence = false; window.isSendingSequence = false;
            }}
            
            function checkQuickReplyTrigger(input) {{
                if(input.value.endsWith("/")) {{
                    const side = document.getElementById('rightSidebar');
                    if(side){{
                        side.style.display = 'flex';
                        cargarQuickReplies();
                        setTimeout(()=> document.getElementById('qrSearchFilter').focus(), 50);
                    }}
                }}
            }}
            
            const _qrSelectedLabels = new Set();
            
            function abrirModalCrearQR(idElement = null) {{
                const m = document.getElementById('qrCreateModal');
                if(!m) return;
                
                document.getElementById('newQrId').value = idElement || '';
                document.getElementById('newQrTitle').value = '';
                document.getElementById('newQrCat').value = 'General';
                document.getElementById('newQrDelay').value = '1500';
                _qrSelectedLabels.clear();
                
                const msgContainer = document.getElementById('qrMessagesContainer');
                msgContainer.innerHTML = '';
                
                if (idElement) {{
                    const qr = quickRepliesCache.find(q => q.id === idElement);
                    if(qr) {{
                        document.getElementById('newQrTitle').value = qr.title || '';
                        document.getElementById('newQrCat').value = qr.category || 'General';
                        document.getElementById('newQrDelay').value = qr.delay_ms || 1500;
                        (qr.etiquetas || []).forEach(t => _qrSelectedLabels.add(t));
                        
                        const msgs = (qr.mensajes && qr.mensajes.length > 0) ? qr.mensajes : [{{type:'text', content: qr.content}}];
                        msgs.forEach(m => {{
                            if(typeof m === 'string') addQrMessageField('text', m);
                            else addQrMessageField(m.type || 'text', m.content || '', m.media_id || null, m.filename || null);
                        }});
                    }}
                }} else {{
                    addQrMessageField('text');
                }}
                
                document.getElementById('modalTitleText').innerText = idElement ? 'Editar Respuesta' : 'Nueva Respuesta';
                _renderQrLabelPicker();
                m.style.display = 'flex';
                setTimeout(() => document.getElementById('newQrTitle').focus(), 50);
            }}
            
            function _renderQrLabelPicker() {{
                const picker = document.getElementById('qrLabelPicker');
                const options = document.getElementById('qrLabelOptions');
                const empty = document.getElementById('qrLabelPickerEmpty');
                if(!picker || !options) return;
                
                // Render selected badges in picker
                picker.querySelectorAll('.qr-sel-badge').forEach(b => b.remove());
                _qrSelectedLabels.forEach(lid => {{
                    const lbl = (window._globalLabels||[]).find(l=>l.id===lid);
                    if(!lbl) return;
                    const badge = document.createElement('span');
                    badge.className = 'qr-sel-badge';
                    badge.style.cssText = `background:${{lbl.color}}22; color:${{lbl.color}}; font-size:0.7rem; padding:0.2rem 0.5rem; border-radius:4px; border:1px solid ${{lbl.color}}44; cursor:pointer; font-weight:600;`;
                    badge.innerText = lbl.name + ' ×';
                    badge.onclick = () => {{ _qrSelectedLabels.delete(lid); _renderQrLabelPicker(); }};
                    picker.appendChild(badge);
                }});
                empty.style.display = _qrSelectedLabels.size > 0 ? 'none' : 'inline';
                
                // Render available options
                options.innerHTML = '';
                (window._globalLabels||[]).forEach(lbl => {{
                    if(_qrSelectedLabels.has(lbl.id)) return;
                    const chip = document.createElement('span');
                    chip.style.cssText = `background:${{lbl.color}}15; color:${{lbl.color}}; font-size:0.7rem; padding:0.2rem 0.5rem; border-radius:4px; border:1px dashed ${{lbl.color}}44; cursor:pointer;`;
                    chip.innerText = '+ ' + lbl.name;
                    chip.onclick = () => {{ _qrSelectedLabels.add(lbl.id); _renderQrLabelPicker(); }};
                    options.appendChild(chip);
                }});
            }}
            
            function addQrMessageField(type = 'text', content = '', mediaId = null, filename = null) {{
                const msgContainer = document.getElementById('qrMessagesContainer');
                const div = document.createElement('div');
                div.style.cssText = 'background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:8px; padding:0.6rem; position:relative;';
                
                const typeColors = {{text:'#10b981', image:'#717f7f', video:'#8b5cf6', audio:'#f59e0b'}};
                const typeIcons = {{text:'📝', image:'🖼', video:'🎬', audio:'🎵'}};
                const color = typeColors[type] || '#10b981';
                const icon = typeIcons[type] || '📝';
                
                div.style.borderLeftColor = color;
                div.style.borderLeftWidth = '3px';
                div.dataset.msgType = type;
                
                let inner = `<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                    <span style="font-size:0.72rem; font-weight:600; color:${{color}};">${{icon}} ${{type.toUpperCase()}}</span>
                    <button type="button" onclick="this.closest('div[data-msg-type]').remove()" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:1rem; padding:0;">×</button>
                </div>`;
                
                if(type === 'text') {{
                    inner += `<textarea rows="2" class="qr-msg-input" style="width:100%; padding:0.5rem; border-radius:5px; border:1px solid var(--accent-border); background:var(--bg-main); color:var(--text-main); outline:none; font-size:0.85rem; resize:vertical; box-sizing:border-box;" placeholder="Escribe el mensaje...">${{content}}</textarea>`;
                }} else if(type === 'action_label') {{
                    const selId = mediaId || '';
                    let opts = `<option value="">-- Seleccionar Etiqueta --</option>`;
                    (window._globalLabels||[]).forEach(l => {{
                        opts += `<option value="${{l.id}}" ${{l.id===selId?'selected':''}}>${{l.name}}</option>`;
                    }});
                    inner += `
                    <div style="display:flex; flex-direction:column; gap:0.4rem; padding:0.4rem; background:rgba(0,0,0,0.1); border-radius:6px; margin-top:0.3rem;">
                        <span style="font-size:0.8rem; color:var(--text-main); font-weight:600;">Acción Automática: Poner/Quitar Etiqueta</span>
                        <span style="font-size:0.7rem; color:var(--text-muted); line-height:1.2;">Al ejecutarse este paso, la etiqueta seleccionada se añadirá al chat (o se quitará si ya existe en él).</span>
                        <select class="qr-action-select qr-media-id" style="width:100%; padding:0.6rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.85rem; cursor:pointer;">
                            ${{opts}}
                        </select>
                    </div>`;
                }} else {{
                    const hasMedia = mediaId && mediaId !== '';
                    const displayName = filename || mediaId || '';
                    const accept = type === 'image' ? 'image/*' : type === 'video' ? 'video/*' : 'audio/*';
                    inner += `
                    <input type="hidden" class="qr-media-id" value="${{hasMedia ? mediaId : ''}}">
                    <div class="qr-media-preview" style="font-size:0.8rem; color:var(--text-muted); padding:0.3rem 0; min-height:24px;">${{hasMedia ? '[OK] ' + displayName : '(sin archivo)'}}</div>
                    <div style="display:flex; gap:0.4rem; margin-top:0.4rem; align-items:center;">
                        <label style="background:rgba(255,255,255,0.07); border:1px solid var(--accent-border); border-radius:5px; padding:0.3rem 0.6rem; cursor:pointer; font-size:0.78rem; color:var(--text-main);">
                            📂 Subir archivo
                            <input type="file" accept="${{accept}}" style="display:none;" onchange="uploadQrMedia(this, '${{type}}')">
                        </label>
                        ${{hasMedia ? `<span style="font-size:0.75rem; color:#10b981;">✓ Listo</span>` : ''}}
                    </div>
                    <textarea rows="1" class="qr-media-caption" style="width:100%; margin-top:0.4rem; padding:0.4rem; border-radius:5px; border:1px solid var(--accent-border); background:var(--bg-main); color:var(--text-main); outline:none; font-size:0.82rem; resize:none; box-sizing:border-box;" placeholder="Pie de foto / caption (opcional)">${{content}}</textarea>`;
                }}
                
                div.innerHTML = inner;
                msgContainer.appendChild(div);
            }}
            
            async function uploadQrMedia(input, mediaType) {{
                const file = input.files[0];
                if(!file) return;
                const container = input.closest('div[data-msg-type]');
                const preview = container.querySelector('.qr-media-preview');
                const hiddenId = container.querySelector('.qr-media-id');
                preview.innerHTML = '⏳ Subiendo...';
                
                const fd = new FormData();
                fd.append('file', file);
                try {{
                    const res = await fetch('/api/quick-replies/upload-media', {{ method:'POST', body: fd }});
                    const d = await res.json();
                    if(d.ok) {{
                        hiddenId.value = d.media_id;
                        preview.innerHTML = `[OK] ${{file.name}} <small style="color:#10b981;">(ID: ${{d.media_id.substring(0,12)}}...)</small>`;
                    }} else {{
                        preview.innerHTML = `[ERROR] Error: ${{d.error}}`;
                    }}
                }} catch(e) {{
                    preview.innerHTML = '[ERROR] Error de red';
                }}
            }}
            
            function insertarVariableQR(variable) {{
                let activeElem = document.activeElement;
                if(!activeElem || !activeElem.classList.contains('qr-msg-input')) {{
                    const textareas = document.querySelectorAll('.qr-msg-input');
                    if(textareas.length === 0) return;
                    activeElem = textareas[textareas.length - 1];
                }}
                const pos = activeElem.selectionStart;
                const txt = activeElem.value;
                activeElem.value = txt.slice(0, pos) + variable + txt.slice(activeElem.selectionEnd);
                activeElem.selectionStart = activeElem.selectionEnd = pos + variable.length;
                activeElem.focus();
            }}

            async function guardarNuevoQR() {{
                const id = document.getElementById('newQrId').value || null;
                const title = document.getElementById('newQrTitle').value.trim();
                const cat = document.getElementById('newQrCat').value.trim() || "General";
                const delay = parseInt(document.getElementById('newQrDelay').value) || 1500;
                
                // Build mensajes array from all message blocks
                const mensajes = [];
                document.querySelectorAll('#qrMessagesContainer > div[data-msg-type]').forEach(block => {{
                    const msgType = block.dataset.msgType;
                    if(msgType === 'text') {{
                        const ta = block.querySelector('.qr-msg-input');
                        if(ta && ta.value.trim()) mensajes.push({{type: 'text', content: ta.value.trim()}});
                    }} else {{
                        const mediaId = block.querySelector('.qr-media-id')?.value?.trim();
                        const caption = block.querySelector('.qr-media-caption')?.value?.trim() || '';
                        if(mediaId) mensajes.push({{type: msgType, media_id: mediaId, content: caption}});
                    }}
                }});
                
                if(!title || mensajes.length === 0) return alert("Se requiere Título y al menos un Mensaje o Media.");
                
                const etiquetas = Array.from(_qrSelectedLabels);
                
                try {{
                    const res = await fetch("/api/quick-replies", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ id, title, mensajes, delay_ms: delay, category: cat, type: "text", etiquetas, line_id: new URLSearchParams(window.location.search).get("line") || "principal" }})
                    }});
                    if(res.ok) {{
                        document.getElementById('qrCreateModal').style.display = 'none';
                        cargarQuickReplies();
                    }} else {{
                        alert("Hubo un error guardando.");
                    }}
                }} catch(e) {{
                    alert("Error guardando QR: " + e.message);
                }}
            }}

            async function eliminarQR(id) {{
                if(!confirm("¿Deseas eliminar definitivamente este atajo?")) return;
                try {{
                    const res = await fetch(`/api/quick-replies/${{id}}`, {{ method: "DELETE" }});
                    if(res.ok) cargarQuickReplies();
                }} catch(e) {{
                    alert("No se pudo eliminar");
                }}
            }}

            </script>
            <script>
            let quickRepliesCache = [];
            async function cargarQuickReplies() {{
                const list = document.getElementById("quickRepliesList");
                if(!list) return;
                list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); text-align:center;">Cargando respuestas...</div>`;
                try {{
                    // Load labels first so cards can render label badges
                    const [resQr, resLbl] = await Promise.all([
                        fetch("/api/quick-replies?line=" + (new URLSearchParams(window.location.search).get("line") || "principal")),
                        fetch("/api/admin/labels/list")
                    ]);
                    if (!resQr.ok) throw new Error("HTTP " + resQr.status);
                    const data = await resQr.json();
                    const lblData = resLbl.ok ? await resLbl.json() : [];
                    window._globalLabels = Array.isArray(lblData) ? lblData : (lblData.labels || []);
                    quickRepliesCache = data;
                    renderQuickReplies(data);
                }} catch(e) {{
                    list.innerHTML = `<div style="font-size:0.85rem; color:red; padding:1rem; text-align:center; background:rgba(255,0,0,0.1); border-radius:8px;">Error: ${{e.message}}</div>`;
                }}
            }}
            function renderQuickReplies(data) {{
                const list = document.getElementById("quickRepliesList");
                if(!list) return;
                if(data.length === 0) {{
                    list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:1rem; text-align:center;">Sin respuestas rápidas en el sistema.</div>`;
                    return;
                }}
                list.innerHTML = "";
                
                // Agrupar por categoría
                const groups = {{}};
                data.forEach(qr => {{
                    const cat = qr.category && qr.category.trim() !== "" ? qr.category : "General";
                    if(!groups[cat]) groups[cat] = [];
                    groups[cat].push(qr);
                }});
                
                // Variables de control de estado abierto (mantener abiertos los grupos al buscar)
                const searchInput = document.getElementById('qrSearchFilter');
                const isSearching = searchInput && searchInput.value.trim() !== "";
                
                Object.keys(groups).sort().forEach(cat => {{
                    const groupContainer = document.createElement("div");
                    groupContainer.style.cssText = "display:flex; flex-direction:column; gap:0.4rem; margin-bottom:0.2rem;";
                    
                    const catHeader = document.createElement("div");
                    catHeader.style.cssText = "background:rgba(255,255,255,0.05); padding:0.6rem 0.8rem; border-radius:6px; cursor:pointer; display:flex; justify-content:space-between; align-items:center; font-weight:600; font-size:0.85rem; border:1px solid var(--accent-border); user-select:none; transition:background 0.2s;";
                    catHeader.onmouseover = function() {{this.style.background='rgba(255,255,255,0.08)';}};
                    catHeader.onmouseout = function() {{this.style.background='rgba(255,255,255,0.05)';}};
                    
                    const catTitle = document.createElement("span");
                    catTitle.innerText = cat + " (" + groups[cat].length + ")";
                    
                    const catIcon = document.createElement("span");
                    catIcon.innerHTML = "▼";
                    catIcon.style.cssText = "font-size:0.75rem; transition:transform 0.2s;";
                    if (!isSearching && cat !== "General" && cat !== "General (0)") {{
                        catIcon.style.transform = "rotate(-90deg)"; // Closed by default unless it's General
                    }}
                    
                    catHeader.appendChild(catTitle);
                    catHeader.appendChild(catIcon);
                    
                    const catContent = document.createElement("div");
                    catContent.style.cssText = "display:flex; flex-direction:column; gap:0.6rem; margin-top:0.2rem;";
                    
                    // Manage default state
                    if (!isSearching && cat !== "General" && cat !== "General (0)") {{
                        catContent.style.display = "none";
                    }}
                    
                    catHeader.onclick = () => {{
                        if (catContent.style.display === "none") {{
                            catContent.style.display = "flex";
                            catIcon.style.transform = "rotate(0deg)";
                        }} else {{
                            catContent.style.display = "none";
                            catIcon.style.transform = "rotate(-90deg)";
                        }}
                    }};
                    
                    groupContainer.appendChild(catHeader);
                    groupContainer.appendChild(catContent);
                    list.appendChild(groupContainer);
                
                    groups[cat].forEach(qr => {{
                        const container = document.createElement("div");
                        container.style.cssText = "display:flex; flex-direction:column; background:var(--accent-bg); padding:0.65rem 0.75rem; border-radius:8px; border:1px solid var(--accent-border); transition:border-color 0.15s; position:relative;";
                        container.onmouseover = function() {{this.style.borderColor='var(--primary-color)';}};
                        container.onmouseout = function() {{this.style.borderColor='var(--accent-border)';}};
                        if (window.ES_ADMIN) {{
                            container.draggable = true;
                            container.dataset.qrId = qr.id;
                            container.title = "Arrastra para reordenar";
                            container.addEventListener("dragstart", function(e) {{
                                e.dataTransfer.effectAllowed = "move";
                                window._draggedQrItem = this;
                                setTimeout(() => this.style.opacity = "0.3", 0);
                            }});
                            container.addEventListener("dragover", function(e) {{
                                e.preventDefault();
                                this.style.borderTop = "2px solid var(--primary-color)";
                            }});
                            container.addEventListener("dragleave", function(e) {{
                                this.style.borderTop = "";
                            }});
                            container.addEventListener("drop", async function(e) {{
                                e.preventDefault(); e.stopPropagation(); this.style.borderTop = "";
                                const dragged = window._draggedQrItem;
                                if (dragged && dragged !== this) {{
                                    const listContainer = this.parentNode;
                                    const items = Array.from(listContainer.children);
                                    if (items.indexOf(dragged) < items.indexOf(this)) listContainer.insertBefore(dragged, this.nextSibling);
                                    else listContainer.insertBefore(dragged, this);
                                    const newOrder = Array.from(listContainer.children).map(c => c.dataset.qrId).filter(id => id);
                                    try {{
                                        const res = await fetch("/api/quick-replies/reorder", {{
                                            method: "POST", headers: {{"Content-Type": "application/json"}},
                                            body: JSON.stringify({{order: newOrder}})
                                        }});
                                        if (res.ok) cargarQuickReplies();
                                    }} catch(err) {{ console.error(err); }}
                                }}
                            }});
                            container.addEventListener("dragend", function() {{
                                this.style.opacity = "1";
                                window._draggedQrItem = null;
                            }});
                        }}
                        const btn = document.createElement("button");
                        btn.type = "button";
                        btn.style.cssText = "background:none; border:none; text-align:left; cursor:pointer; color:var(--text-main); width:100%; display:flex; flex-direction:column; gap:0.25rem;";
                        const headerRow = document.createElement("div");
                        headerRow.style.cssText = "display:flex; justify-content:space-between; align-items:center; width:100%;";
                        const titleWrap = document.createElement("div");
                        titleWrap.style.cssText = "display:flex; align-items:center; gap:0.4rem; flex-wrap:wrap;";
                        const titleEl = document.createElement("strong");
                        titleEl.innerText = qr.title || qr.category || '(sin título)';
                        titleEl.style.fontSize = "0.88rem";
                        titleWrap.appendChild(titleEl);
                        const editBtn = document.createElement("button");
                        editBtn.innerHTML = "✎";
                        editBtn.title = "Editar";
                        editBtn.style.cssText = "background:none; border:none; color:var(--primary-color); cursor:pointer; padding:0 0.2rem; font-size:0.9rem; margin-right:1.4rem; flex-shrink:0;";
                        editBtn.onclick = (e) => {{ e.stopPropagation(); abrirModalCrearQR(qr.id); }};
                        headerRow.appendChild(titleWrap);
                        if (window.ES_ADMIN) {{ headerRow.appendChild(editBtn); }}
                        btn.appendChild(headerRow);
                        const msgs = qr.mensajes || [];
                        const previewParts = msgs.slice(0,3).map(m => {{
                            if(typeof m === 'string') return m;
                            if(m.type === 'text') return m.content || '';
                            if(m.type === 'image') return '🖼 Imagen';
                            if(m.type === 'video') return '🎬 Video';
                            if(m.type === 'audio') return '🎵 Audio';
                            return '[media]';
                        }});
                        const prev = document.createElement("span");
                        prev.style.cssText = "font-size:0.78rem; color:var(--text-muted); line-height:1.3; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;";
                        const lenStr = msgs.length > 1 ? ` (${{msgs.length}} msgs)` : '';
                        prev.innerText = previewParts.join(' → ') + (msgs.length > 3 ? ' ...' : '') + lenStr;
                        btn.appendChild(prev);
                        if(qr.etiquetas && qr.etiquetas.length > 0) {{
                            const labelsRow = document.createElement("div");
                            labelsRow.style.cssText = "display:flex; flex-wrap:wrap; gap:0.3rem; margin-top:0.2rem;";
                            qr.etiquetas.forEach(lid => {{
                                const lbl = (window._globalLabels||[]).find(l=>l.id===lid);
                                if(!lbl) return;
                                const badge = document.createElement("span");
                                badge.style.cssText = `background:${{lbl.color}}22; color:${{lbl.color}}; font-size:0.62rem; padding:0.1rem 0.35rem; border-radius:3px; border:1px solid ${{lbl.color}}44; font-weight:600;`;
                                badge.innerText = lbl.name;
                                labelsRow.appendChild(badge);
                            }});
                            btn.appendChild(labelsRow);
                        }}
                        btn.onclick = () => aplicarQuickReply(qr.id);
                        container.appendChild(btn);
                        if (window.ES_ADMIN) {{
                            const delBtn = document.createElement("button");
                            delBtn.innerHTML = "×";
                            delBtn.title = "Eliminar";
                            delBtn.style.cssText = "position:absolute; top:0.4rem; right:0.4rem; background:rgba(0,0,0,0.3); border:none; color:#ef4444; border-radius:50%; width:18px; height:18px; display:flex; justify-content:center; align-items:center; cursor:pointer; opacity:0; transition:opacity 0.2s; font-size:0.75rem;";
                            container.onmouseenter = () => {{ delBtn.style.opacity = "1"; }};
                            container.onmouseleave = () => {{ delBtn.style.opacity = "0"; }};
                            delBtn.onclick = (e) => {{ e.stopPropagation(); eliminarQR(qr.id); }};
                            container.appendChild(delBtn);
                        }}
                        catContent.appendChild(container);
                    }});
                }});
            }}

        function filtrarQuickReplies(val) {{
                const valLower = val.toLowerCase();
                const filt = quickRepliesCache.filter(q => q.title?.toLowerCase().includes(valLower) || q.content?.toLowerCase().includes(valLower));
                renderQuickReplies(filt);
            }}
            </script>
                        <script>
            var c = document.getElementById('chatScroll');
            if(c) {{
                const params = new URLSearchParams(window.location.search);
                const msgId = params.get('msg_id');
                if (msgId) {{
                    // Historial completo cargado: el polling seguira pidiendo history=all
                    window._viewingAllHistory = true;

                    // Limpiar param de URL sin recargar
                    const url = new URL(window.location);
                    url.searchParams.delete('msg_id');
                    window.history.replaceState({{}}, '', url);

                    let attempts = 0;
                    function tryScroll() {{
                        const el = document.getElementById('msg-' + msgId);
                        if (el) {{
                            requestAnimationFrame(() => requestAnimationFrame(() => {{
                                // Scroll inicial (instant para evitar que smooth quede a medias)
                                el.scrollIntoView({{ behavior: 'instant', block: 'center' }});

                                // Highlight visual
                                el.style.transition = 'all 0.5s ease';
                                el.style.boxShadow = '0 0 0 4px var(--primary-color)';
                                el.style.transform = 'scale(1.02)';

                                // Re-scroll progresivo: las imagenes cargan y desplazan el layout
                                // Corregir en 4 momentos hasta que el layout se estabilice
                                [400, 900, 1600, 2600].forEach(delay => {{
                                    setTimeout(() => {{
                                        const target = document.getElementById('msg-' + msgId);
                                        if (target) target.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                                    }}, delay);
                                }});

                                // Quitar highlight despues de 3.5s
                                setTimeout(() => {{
                                    el.style.boxShadow = '';
                                    el.style.transform = 'scale(1)';
                                }}, 3500);
                            }}));
                        }} else if (attempts < 40) {{
                            attempts++;
                            setTimeout(tryScroll, 150);
                        }} else {{
                            c.scrollTop = c.scrollHeight;
                        }}
                    }}
                    tryScroll();
                }} else {{
                    c.scrollTop = c.scrollHeight;
                }}
            }}
        </script>
        """

        chat_view_css = """
        .bubble { max-width:85%; padding:0.8rem 1rem; border-radius:12px; font-size:0.95rem; line-height:1.4; position:relative; word-wrap:break-word; overflow-wrap:anywhere; box-sizing:border-box; }
        .lado-izq { align-self:flex-start; }
        .lado-der { align-self:flex-end; }
        .bubble-bot { background:var(--primary-color); color:var(--text-main); border-bottom-right-radius:4px; }
        .bubble-user { background:var(--accent-bg); color:var(--text-main); border-bottom-left-radius:4px; border:1px solid var(--accent-border); }
        .bubble-sticker { background:transparent !important; border:none !important; padding:0 !important; box-shadow:none !important; }
        """

    # Reemplazos finales en la plantilla
    es_chat_valido = bool(wa_id and wa_id in sesiones)
    html = html.replace("{body_class}", "view-chat" if es_chat_valido else "view-list")
    html = html.replace("{tab_all_active}", "active" if tab not in ("human", "archived") else "")
    html = html.replace("{tab_human_active}", "active" if tab == "human" else "")
    html = html.replace("{tab_archived_active}", "active" if tab == "archived" else "")
    html = html.replace("{lista_chats_html}", lista_chats_html)
    html = html.replace("{labels_filter_html}", labels_filter_html)
    html = html.replace("{chat_viewer_html}", chat_viewer_html)
    if s_fake_vg:
        html = html.replace("{style_input_area}", 'style="display:none;"')
        html = html.replace("{grupo_virtual_banner}", '''<div style="padding:0.75rem; background:rgba(168,85,247,0.1); border-top:1px solid rgba(168,85,247,0.3); color:#c084fc; text-align:center; font-size:0.85rem; font-weight:600;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:middle; margin-right:5px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg> GRUPO VIRTUAL DE SOLO LECTURA. HAZ CLIC EN EL LOGO/FOTO AL LADO DE UN MENSAJE PARA ABRIR SU CHAT PRIVADO.</div>''')
    else:
        html = html.replace("{style_input_area}", '')
        html = html.replace("{grupo_virtual_banner}", '')
    html = html.replace("{chat_view_css}", chat_view_css)
    html = html.replace("{color_global}", "#10b981" if BOT_GLOBAL_ACTIVO else "#ef4444")
    
    # Tema Custom
    custom_theme_css = ""
    usuario_sesion = obtener_usuario_sesion(request)
    if usuario_sesion and "preferencias_ui" in usuario_sesion:
        prefs = usuario_sesion["preferencias_ui"]
        c_bg = prefs.get('bg_main', '#213668')
        c_prim = prefs.get('primary_color', '#717f7f')
        c_acc = prefs.get('accent_bg', '#ffffff')
        
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

    html = html.replace("{custom_theme_css}", custom_theme_css)

    return HTMLResponse(inyectar_tema_global(request, html))

@app.post("/api/user/theme")
async def update_user_theme(
    request: Request, 
    bg_main: str = Form(None), 
    accent_bg: str = Form(None), 
    primary_color: str = Form(None), 
    text_main: str = Form(None),
    text_muted: str = Form(None),
    wallpaper: str = Form(None), 
    wallpaper_opacity: str = Form("0.15"),
    wallpaper_offset_y: str = Form("50"),
    wallpaper_offset_x: str = Form("50"),
    wallpaper_file: UploadFile = File(None)
):
    if not verificar_sesion(request):
        return {"ok": False, "error": "No autorizado"}
    
    usuario_sesion = obtener_usuario_sesion(request)
    if not usuario_sesion: return {"ok": False}
    
    # Manejar subida de archivo si existe
    if wallpaper_file and wallpaper_file.filename:
        ext = wallpaper_file.filename.split(".")[-1].lower()
        if ext in ["mp4", "webm"]:
            import os
            os.makedirs("static/wallpapers", exist_ok=True)
            filename = f"wp_{usuario_sesion.get('username', 'user')}_{int(datetime.utcnow().timestamp())}.{ext}"
            file_path = f"static/wallpapers/{filename}"
            content = await wallpaper_file.read()
            if len(content) > 10 * 1024 * 1024:
                return {"ok": False, "error": "El video supera los 10MB"}
            with open(file_path, "wb") as f:
                f.write(content)
            wallpaper = f"/{file_path}"
        else:
            from firebase_client import guardar_wallpaper_en_bd
            filename = f"wp_{usuario_sesion.get('username', 'user')}_{int(datetime.utcnow().timestamp())}.{ext}"
            content = await wallpaper_file.read()
            guardar_wallpaper_en_bd(filename, content, ext)
            wallpaper = f"/api/media/wallpaper/{filename}"

    prefs = {
        "bg_main": bg_main or "#0f172a",
        "accent_bg": accent_bg or "#1e293b",
        "primary_color": primary_color or "#717f7f",
        "text_main": text_main or "#f8fafc",
        "text_muted": text_muted or "#94a3b8",
        "wallpaper": wallpaper or "",
        "wallpaper_opacity": wallpaper_opacity or "0.15",
        "wallpaper_offset_y": wallpaper_offset_y or "50",
        "wallpaper_offset_x": wallpaper_offset_x or "50"
    }
    
    username = usuario_sesion.get("username")
    if username:
        from firebase_client import actualizar_preferencias_tema
        actualizar_preferencias_tema(username, prefs)
        usuario_sesion["preferencias_ui"] = prefs
        save_sessions()
        
    return {"ok": True}

@app.get("/inbox", response_class=HTMLResponse)
async def inbox_main(request: Request, tab: str = "all", label: str = None, unread: str = None, line: str = "all"):
    return renderizar_inbox(request, None, tab, label, unread, line)

from typing import List

@app.post("/api/admin/stickers/upload")
async def upload_stickers(files: List[UploadFile] = File(...)):
    """Recibe múltiples archivos webp/png y los guarda directamente a Firestore."""
    try:
        import os
        from firebase_client import guardar_sticker_en_bd
        count = 0
        for file in files:
            if file.filename.endswith(".webp") or file.filename.endswith(".png"):
                # Extraemos solo el nombre del archivo, ignorando subcarpetas
                basename = os.path.basename(file.filename)
                content = await file.read()
                
                # Guardar en Base de Datos (Persistente)
                guardar_sticker_en_bd(basename, content)
                
                count += 1
        return {"ok": True, "count": count}
    except Exception as e:
        return {"ok": False, "error": str(e)}

from pydantic import BaseModel
class SaveMediaPayload(BaseModel):
    media_id: str

@app.post("/api/admin/stickers/save_from_media")
async def save_sticker_media(payload: SaveMediaPayload, request: Request):
    """Guarda un sticker enviado por el usuario a la galería global de favoritos."""
    if not verificar_sesion(request):
        return {"ok": False, "error": "No autorizado"}
        
    media_id = payload.media_id
    from whatsapp_client import obtener_media_url, descargar_media
    url = await obtener_media_url(media_id)
    if not url: return {"ok": False, "error": "Archivo no ubicado en WhatsApp Meta"}
    
    contenido, mime_type = await descargar_media(url)
    if not contenido: return {"ok": False, "error": "No se pudo descargar content"}
    
    from firebase_client import guardar_sticker_en_bd
    basename = f"fav_{media_id}.webp"
    
    guardar_sticker_en_bd(basename, contenido)
    return {"ok": True, "filename": basename}


class TranscribePayload(BaseModel):
    wa_id: str
    msg_id: str

@app.post("/api/transcribe/{media_id}")
async def api_transcribe(media_id: str, payload: TranscribePayload, request: Request):
    if not verificar_sesion(request):
        return {"ok": False, "error": "No autorizado"}
    
    wa_id = payload.wa_id
    msg_id = payload.msg_id
    
    if wa_id not in sesiones:
        return {"ok": False, "error": "Sesion no encontrada"}
        
    await cachear_media(media_id)
    if media_id not in media_cache:
        return {"ok": False, "error": "No se pudo obtener el audio"}
        
    contenido, mime = media_cache[media_id]
    
    try:
        from google.genai import types
        part = types.Part.from_bytes(data=contenido, mime_type="audio/ogg")
        res = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[part, "Transcribe exactamente lo que se dice en este audio. Sin comentarios tuyos, solo la transcripción limpia. Si está ininteligible, escribe '[Audio ininteligible]'. Manten el idioma original del audio."]
        )
        transcripcion = res.text.strip()
    except Exception as e:
        return {"ok": False, "error": f"Fallo al transcribir: {str(e)}"}
        
    # Guardar persistencia
    encontrado = False
    for msg in sesiones[wa_id].get("historial", []):
        if msg.get("msg_id") == msg_id or msg.get("id") == msg_id:
            msg["transcripcion"] = transcripcion
            encontrado = True
            break
            
    if encontrado:
        from firebase_client import guardar_sesion_chat
        guardar_sesion_chat(wa_id, sesiones[wa_id])
        return {"ok": True, "transcripcion": transcripcion}
    else:
        return {"ok": False, "error": "Mensaje no encontrado en historial"}


@app.get("/api/stickers")
def get_stickers():
    """Retorna la lista de stickers webp disponibles dinámicamente desde Firestore."""
    try:
        from firebase_client import obtener_todos_los_nombres_stickers
        stickers = obtener_todos_los_nombres_stickers()
        # Filter to webp or png to be safe
        stickers = [f for f in stickers if f.endswith(".webp") or f.endswith(".png")]
        return {"ok": True, "stickers": stickers}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/api/media/sticker/{filename}")
def get_sticker_image(filename: str):
    from firebase_client import obtener_sticker_de_bd
    from fastapi.responses import Response
    bytes_data = obtener_sticker_de_bd(filename)
    if bytes_data is None:
        return Response(status_code=404, content="Not found")
    media_type = "image/webp" if filename.endswith(".webp") else "image/png"
    return Response(content=bytes_data, media_type=media_type, headers={"Cache-Control": "public, s-maxage=31536000, max-age=31536000"})

@app.get("/api/media/wallpaper/{filename}")
def get_wallpaper_image(filename: str):
    from firebase_client import obtener_wallpaper_de_bd
    from fastapi.responses import Response
    bytes_data = obtener_wallpaper_de_bd(filename)
    if bytes_data is None:
        return Response(status_code=404, content="Not found")
    ext = filename.split(".")[-1].lower()
    media_type = f"image/{ext}" if ext in ["jpeg", "jpg", "png", "webp", "gif"] else "application/octet-stream"
    if media_type == "image/jpg": media_type = "image/jpeg"
    return Response(content=bytes_data, media_type=media_type, headers={"Cache-Control": "public, s-maxage=31536000, max-age=31536000"})


@app.get("/inbox/{wa_id}", response_class=HTMLResponse)
async def inbox_chat(request: Request, wa_id: str, tab: str = "all", label: str = None, unread: str = None, line: str = "all"):
    return renderizar_inbox(request, wa_id, tab, label, unread, line)

@app.get("/debug")
async def debug_sesiones():
    """Endpoint temporal para inspeccionar sesiones activas."""
    resultado = {}
    for num, s in sesiones.items():
        historial_resumido = [
            {"role": m["role"], "preview": m["content"][:100]}
            for m in s["historial"]
            if m["role"] != "system"
        ]
        resultado[num] = {
            "nombre": s.get("nombre_cliente"),
            "bot_activo": s.get("bot_activo"),
            "lineId": s.get("lineId"),
            "numero_real": s.get("numero_real"),
            "is_archived": s.get("is_archived", False),
            "pedido_id": s.get("datos_pedido", {}).get("id") if s.get("datos_pedido") else None,
        }
    return resultado


# ─────────────────────────────────────────────
#  Simulador Web de Chat
# ─────────────────────────────────────────────

@app.get("/simulador", response_class=HTMLResponse)
async def pagina_simulador(request: Request):
    """Interfaz web para probar el comportamiento del bot."""
    if not verificar_sesion(request):
        return RedirectResponse(url=f"/admin", status_code=302)
    return HTMLResponse("""
    <html>
    <head>
      <title>Simulador de WhatsApp</title>
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
      <style>
        :root {
          --wa-bg: #ece5dd; --wa-chat-bg: #e5ddd5; --wa-header: #075e54;
          --wa-me: #dcf8c6; --wa-bot: #ffffff; --text-dark: #111b21; --text-gray: #667781;
        }
        * {box-sizing:border-box;margin:0;padding:0;}
        body {font-family:'Inter',sans-serif;background:#202c33;height:100vh;display:flex;align-items:center;justify-content:center;}
        .app {width:100%;max-width:900px;height:90vh;display:flex;background:white;border-radius:12px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,0.5);}
        .sidebar {width:300px;background:#f0f2f5;border-right:1px solid #d1d7db;display:flex;flex-direction:column;z-index:10;}
        .sidebar-header {background:#f0f2f5;height:60px;padding:1rem;display:flex;align-items:center;font-weight:600;border-bottom:1px solid #d1d7db;color:#111b21;}
        .sidebar-content {padding:1.5rem 1rem;flex:1;display:flex;flex-direction:column;gap:1.5rem;}
        .input-group {display:flex;flex-direction:column;gap:0.4rem;}
        .input-group label {font-size:0.8rem;color:var(--text-gray);font-weight:600;}
        .input-group input {padding:0.75rem 1rem;border:1px solid #d1d7db;border-radius:8px;font-size:0.95rem;outline:none;}
        .input-group input:focus {border-color:#00a884;}
        .btn-limpiar {background:white;border:1px solid #d1d7db;padding:0.6rem;border-radius:8px;cursor:pointer;font-weight:600;color:#54656f;}
        .btn-limpiar:hover {background:#f5f6f6;}
        
        .chat-section {flex:1;display:flex;flex-direction:column;background-color:var(--wa-chat-bg);
                       background-image: url('data:image/svg+xml,%3Csvg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath d="M20 20.5V18H0v-2h20v-2H0v-2h20v-2H0V8h20V6H0V4h20V2H0V0h22v20h2V0h2v20h2V0h2v20h2V0h2v20h2V0h2v20h2V0h2v20h2v2H20v-1.5zM0 20h2v20H0V20zm4 0h2v20H4V20zm4 0h2v20H8V20zm4 0h2v20h-2V20zm4 0h2v20h-2V20zm4 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2z" fill="%23dfd8d1" fill-opacity="0.4" fill-rule="evenodd"/%3E%3C/svg%3E');}
        
        .chat-header {background:#f0f2f5;height:60px;padding:1rem;display:flex;align-items:center;font-weight:600;border-bottom:1px solid #d1d7db;}
        .chat-area {flex:1;padding:2rem 4%;overflow-y:auto;display:flex;flex-direction:column;gap:0.5rem;}
        .chat-input-area {background:#f0f2f5;padding:0.75rem 1rem;display:flex;gap:1rem;align-items:center;}
        .chat-input {flex:1;padding:0.75rem 1.25rem;border-radius:24px;border:none;outline:none;font-size:1rem;background:white;}
        .send-btn {background:#00a884;color:white;border:none;width:45px;height:45px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background 0.2s;}
        .send-btn:hover {background:#017b61;}
        .send-btn:disabled {background:#aaa;cursor:not-allowed;}
        
        /* Burbujas */
        .msg {max-width:75%;display:flex;flex-direction:column;position:relative;margin-bottom:0.3rem;}
        .msg-user {align-self:flex-end;background:var(--wa-me);border-radius:12px 0 12px 12px;padding:0.5rem 0.75rem;box-shadow:0 1px 1px rgba(0,0,0,0.1);color:var(--text-dark);}
        .msg-bot {align-self:flex-start;background:var(--wa-bot);border-radius:0 12px 12px 12px;padding:0.5rem 0.75rem;box-shadow:0 1px 1px rgba(0,0,0,0.1);color:var(--text-dark);}
        .msg-user::before {content:"";position:absolute;top:0;right:-8px;border-left:8px solid var(--wa-me);border-bottom:8px solid transparent;}
        .msg-bot::before {content:"";position:absolute;top:0;left:-8px;border-right:8px solid var(--wa-bot);border-bottom:8px solid transparent;}
        .typing {font-style:italic;color:var(--text-gray);font-size:0.85rem;}
        
        @media(max-width:768px){ .app{height:100vh;flex-direction:column;border-radius:0;} .sidebar{width:100%;height:auto;padding-bottom:1rem;border-right:none;border-bottom:1px solid #ccc;} }
      </style>
    </head>
    <body>
      <div class="app">
        <div class="sidebar">
          <div class="sidebar-header">⚙️ Configuración del Test</div>
          <div class="sidebar-content">
            <div class="input-group">
              <label>Teléfono a simular (WA)</label>
              <input type="text" id="sim-numero" value="51999999991">
            </div>
            <div class="input-group">
              <label>Nombre del Cliente</label>
              <input type="text" id="sim-nombre" value="Tester Local">
            </div>
            <p style="font-size:0.85rem;color:var(--text-gray);line-height:1.5">
              Este chat emula al servidor conectándose a Firebase y consultando a Groq, pero <b>no enviará el mensaje real a tu teléfono</b> a través de la API de Meta.
            </p>
          </div>
        </div>
        
        <div class="chat-section">
          <div class="chat-header">
            Bot IA-ATC — Entorno de Prueba Local
            <a href="/admin" style="margin-left:auto; text-decoration:none; color:var(--text-gray); font-size:0.85rem; font-weight:500">← Volver al Panel</a>
          </div>
          <div class="chat-area" id="chat">
            <div class="msg msg-bot">
              ¡Hola! Escribe aquí para probar el bot. Utiliza un número que tenga pedido en tu base de datos para probar la búsqueda.
            </div>
          </div>
          <div class="chat-input-area">
            <input type="text" id="mensaje" class="chat-input" placeholder="Escribe un mensaje de prueba..." autofocus onkeypress="handleEnter(event)">
            <button id="send-btn" class="send-btn" onclick="sendMessage()">➤</button>
          </div>
        </div>
      </div>
      
      <script>
        const chat = document.getElementById('chat');
        const inputMsg = document.getElementById('mensaje');
        const inputNum = document.getElementById('sim-numero');
        const inputNom = document.getElementById('sim-nombre');
        const sendBtn = document.getElementById('send-btn');
        
        function handleEnter(e) {
            if(e.key === 'Enter') sendMessage();
        }
        
        async function sendMessage() {
            const texto = inputMsg.value.trim();
            if(!texto) return;
            
            const numero = inputNum.value.trim();
            const nombre = inputNom.value.trim();
            
            addMessage(texto, 'msg-user');
            inputMsg.value = '';
            
            const typingId = 'typing-' + Date.now();
            addTyping(typingId);
            sendBtn.disabled = true;
            
            try {
                const res = await fetch('/api/simulador/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ numero, nombre, mensaje: texto })
                });
                
                const data = await res.json();
                removeTyping(typingId);
                
                if(data.respuesta) {
                    addMessage(data.respuesta, 'msg-bot');
                } else {
                    addMessage("<span style='color:#a0a0a0;font-style:italic'>(El bot no ha respondido. Quizás está apagado, o el pedido está en Diseño)</span>", 'msg-bot');
                }
            } catch(error) {
                removeTyping(typingId);
                addMessage("<span style='color:red'>[WARN] Error de conexión</span>", 'msg-bot');
            }
            sendBtn.disabled = false;
            inputMsg.focus();
        }
        
        function addMessage(texto, cssClass) {
            const div = document.createElement('div');
            div.className = `msg ${cssClass}`;
            div.innerHTML = texto.replace(/\\n/g, '<br>');
            chat.appendChild(div);
            scrollBottom();
        }
        
        function addTyping(id) {
            const div = document.createElement('div');
            div.className = `msg msg-bot typing`;
            div.id = id;
            div.innerText = 'escribiendo...';
            chat.appendChild(div);
            scrollBottom();
        }
        
        function removeTyping(id) {
            const div = document.getElementById(id);
            if(div) div.remove();
        }
        
        function scrollBottom() {
            chat.scrollTop = chat.scrollHeight;
        }
      </script>
    </html>
    """)

@app.post("/api/simulador/send")
async def api_simular_mensaje(request: Request):
    """Recibe el mensaje falso del simulador y procesa la lógica nativa del webhook."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")
        
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")

    numero = data.get("numero", "51999999991")
    nombre = data.get("nombre", "Tester")
    texto = data.get("mensaje", "")
    
    print(f"\n{'─'*50}")
    print(f"🧪 SIMULADOR | {nombre} ({numero}): {texto}")
    
    respuesta = procesar_mensaje_interno(numero, nombre, texto, is_simulacion=True)
    
    return {"status": "ok", "respuesta": respuesta}

# ============================================================
#  API DE GESTOR DE PLANTILLAS
# ============================================================

class TemplatePayload(BaseModel):
    name: str
    language: str = "es"
    line_id: str = "principal"

@app.post("/api/admin/templates/save")
async def api_save_template(payload: TemplatePayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import guardar_plantilla_bd
    guardar_plantilla_bd(payload.name, payload.language, payload.line_id)
    return {"ok": True}

@app.post("/api/admin/templates/delete")
async def api_delete_template(payload: TemplatePayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import eliminar_plantilla_bd
    eliminar_plantilla_bd(payload.name)
    return {"ok": True}

@app.get("/api/admin/templates/list")
async def api_list_templates(request: Request, line_id: str = None):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import cargar_plantillas_bd
    plantillas = cargar_plantillas_bd(line_id)
    return {"ok": True, "plantillas": plantillas}

class LineAliasPayload(BaseModel):
    id: str
    name: str
    bot_id: str | None = None
    provider: str | None = None
    meta_phone_id: str | None = None
    meta_token: str | None = None

@app.get("/api/admin/lines")
async def api_list_lines(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    import json
    import os
    aliases = {}
    try:
        if os.path.exists("line_aliases.json"):
            with open("line_aliases.json", "r") as f:
                aliases = json.load(f)
    except: pass
    
    if "principal" not in aliases:
        aliases["principal"] = {"name": "Línea Principal Meta"}
        
    try:
        from server import get_qr_status
        qr_status = get_qr_status()
        if qr_status.get("status") == "connected":
            qr_line_id = qr_status.get("lineId", "qr_ventas_1")
            if qr_line_id not in aliases:
                aliases[qr_line_id] = {"name": "Bot Ventas (Baileys Web)", "provider": "baileys"}
    except Exception as e:
        pass
        
    from bot_manager import get_bot_for_line
    lines_rich = {}
    for lid, linfo in aliases.items():
        if isinstance(linfo, str):
            linfo = {"name": linfo}  # Migration from old string format
            
        lname = linfo.get("name", "undefined")
        provider = linfo.get("provider", "meta" if lid == "principal" else "")
        meta_phone_id = linfo.get("meta_phone_id", "")
        meta_token_has_value = bool(linfo.get("meta_token"))
        
        lines_rich[lid] = {
            "name": lname,
            "provider": provider,
            "meta_phone_id": meta_phone_id,
            "has_meta_token": meta_token_has_value, # Nunca devolver el token crudo a la UI por seguridad
            "bot_id": get_bot_for_line(lid)
        }
        
    return {"ok": True, "lines": lines_rich}

@app.post("/api/admin/lines")
async def api_save_line(payload: LineAliasPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    import json
    import os
    aliases = {}
    try:
        if os.path.exists("line_aliases.json"):
            with open("line_aliases.json", "r") as f:
                aliases = json.load(f)
    except: pass
    
    # Init if needed or map string
    if payload.id not in aliases or isinstance(aliases[payload.id], str):
        aliases[payload.id] = {}
        
    aliases[payload.id]["name"] = payload.name
    
    if payload.provider:
        aliases[payload.id]["provider"] = payload.provider
    if payload.meta_phone_id:
        aliases[payload.id]["meta_phone_id"] = payload.meta_phone_id
    if payload.meta_token: # si envían explicitamente un token, sobreescribir
        aliases[payload.id]["meta_token"] = payload.meta_token

    with open("line_aliases.json", "w") as f:
        json.dump(aliases, f, ensure_ascii=False, indent=2)
        
    from bot_manager import set_bot_for_line
    set_bot_for_line(payload.id, payload.bot_id)
        
    return {"ok": True}

@app.get("/api/bots/config")
async def api_get_bots_config(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from bot_manager import _load_config
    return {"ok": True, "config": _load_config()}

class BotConfigPayload(BaseModel):
    config: dict

@app.post("/api/bots/config")
async def api_save_bots_config(payload: BotConfigPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from bot_manager import _save_config
    try:
        _save_config(payload.config)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.delete("/api/admin/lines/{line_id}")
async def api_delete_line(line_id: str, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    import json, os
    aliases = {}
    try:
        if os.path.exists("line_aliases.json"):
            with open("line_aliases.json", "r") as f:
                aliases = json.load(f)
    except: pass
    if line_id in aliases:
        del aliases[line_id]
        with open("line_aliases.json", "w") as f:
            json.dump(aliases, f, ensure_ascii=False, indent=2)
        return {"ok": True}
    return {"ok": False, "error": "Línea no encontrada"}

class EnviarPlantillaPayload(BaseModel):
    wa_id: str
    template_name: str
    language_code: str = "es"
    body_params: list[str] = None


@app.post("/api/admin/enviar_plantilla")
async def api_enviar_plantilla(payload: EnviarPlantillaPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
        
    
    from whatsapp_client import enviar_plantilla
    wamid = await enviar_plantilla(payload.wa_id, payload.template_name, payload.language_code, payload.body_params)

    
    if wamid:
        # PULL FROM MEMORY (not just firestore) so the Dashboard immediately sees the template
        s = obtener_o_crear_sesion(payload.wa_id)
        
        import urllib.request, json
        from config import META_ACCESS_TOKEN
        tpl_full_text = payload.template_name
        try:
            req = urllib.request.Request(
                f'https://graph.facebook.com/v19.0/1672706204042046/message_templates?name={payload.template_name}',
                headers={'Authorization': 'Bearer ' + META_ACCESS_TOKEN}
            )
            data = json.loads(urllib.request.urlopen(req).read().decode())
            for t in data.get('data', []):
                if t.get('language') == payload.language_code:
                    body_text = ""
                    for c in t.get('components', []):
                        if c['type'] == 'HEADER' and c.get('format') == 'TEXT': body_text += f"{c['text']}\n"
                        elif c['type'] == 'BODY': body_text += f"{c['text']}\n"
                        elif c['type'] == 'FOOTER': body_text += f"\n{c['text']}\n"
                        elif c['type'] == 'BUTTONS':
                            body_text += "\n"
                            for b in c.get('buttons', []): body_text += f"🔘 {b.get('text')}\n"
                    if body_text: tpl_full_text = f"{payload.template_name}\n{body_text.strip()}"
                    break
        except Exception:
            pass
            
        s["historial"].append({"role": "assistant", "content": f"[Plantilla enviada: {tpl_full_text}]", "msg_id": wamid})
        from datetime import datetime
        s["ultima_actividad"] = datetime.utcnow()
        try:
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(payload.wa_id, s)
        except Exception as e:
            print(f"Error guardando sesión en BD tras enviar plantilla: {e}")
            
        return {"ok": True, "wamid": wamid}
    return {"ok": False, "error": "No se pudo enviar (Verifica que la Plantilla ya haya sido aprobada por Meta)."}


# ============================================================
#  API DE GESTOR DE ETIQUETAS Y ASIGNACIONES
# ============================================================

from typing import Optional

class InitChatPayload(BaseModel):
    wa_id: str

@app.post("/api/admin/chat/init")
async def api_init_chat(payload: InitChatPayload, request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    # Meta siempre entrega mensajes con código de país completo (ej: "51997778512").
    # Usamos ese mismo formato como clave de sesión para que coincida.
    digitos = payload.wa_id.replace("+", "").replace(" ", "").strip()
    # Si son 9 dígitos peruanos sin código de país, agregar 51
    if len(digitos) == 9 and not digitos.startswith("51"):
        digitos = "51" + digitos
    obtener_o_crear_sesion(digitos)
    return {"ok": True, "wa_id": digitos}


@app.post("/api/admin/merge_sessions")
async def api_merge_sessions(request: Request):
    """Fusiona sesiones duplicadas: 997778512 + 51997778512 → 51997778512.
    Se ejecuta una sola vez para limpiar datos históricos.
    """
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    if not es_admin(request): raise HTTPException(status_code=403, detail="Solo administradores")

    from firebase_client import guardar_sesion_chat, cargar_sesion_chat, inicializar_firebase

    merged = []
    renamed = []

    # Detectar todas las sesiones de 9 dígitos que tienen un gemelo de 11 dígitos con 51
    keys_9 = [k for k in list(sesiones.keys()) if len(k) == 9 and k.isdigit()]

    for short_key in keys_9:
        long_key = "51" + short_key
        s_short = sesiones.get(short_key, {})

        if long_key in sesiones:
            # CASO A: ambos existen en RAM → fusionar historial
            s_long  = sesiones[long_key]
            hist_combined = s_short.get("historial", []) + s_long.get("historial", [])
            # Deduplicar por msg_id y ordenar por timestamp
            seen = set()
            hist_dedup = []
            for m in hist_combined:
                mid = m.get("msg_id") or id(m)
                if mid not in seen:
                    seen.add(mid)
                    hist_dedup.append(m)
            hist_dedup.sort(key=lambda x: x.get("timestamp", 0))

            # Merge: prevalece la sesión larga, absorbe datos de la corta
            s_long["historial"] = hist_dedup
            if not s_long.get("nombre_cliente") or s_long["nombre_cliente"] == long_key:
                s_long["nombre_cliente"] = s_short.get("nombre_cliente", long_key)

            # Borrar sesión corta de RAM
            del sesiones[short_key]

            # Guardar sesión larga en Firebase
            try:
                guardar_sesion_chat(long_key, s_long)
            except Exception as e:
                print(f"[MERGE] Error guardando {long_key}: {e}")

            # Borrar sesión corta de Firebase
            try:
                db = inicializar_firebase()
                db.collection("chats_atc").document(short_key).delete()
            except Exception as e:
                print(f"[MERGE] Error borrando {short_key} de Firebase: {e}")

            merged.append({"fusionado": f"{short_key} + {long_key}", "mensajes": len(hist_dedup)})
            print(f"[MERGE] ✅ Fusionados {short_key} + {long_key} ({len(hist_dedup)} msgs)")

        else:
            # CASO B: solo existe la corta → renombrar a la larga
            sesiones[long_key] = s_short
            del sesiones[short_key]

            try:
                guardar_sesion_chat(long_key, s_short)
            except Exception as e:
                print(f"[MERGE] Error guardando {long_key}: {e}")

            try:
                db = inicializar_firebase()
                db.collection("chats_atc").document(short_key).delete()
            except Exception as e:
                print(f"[MERGE] Error borrando {short_key}: {e}")

            renamed.append({"renombrado": f"{short_key} → {long_key}"})
            print(f"[MERGE] 🔄 Renombrado {short_key} → {long_key}")

    return {
        "ok": True,
        "fusionados": merged,
        "renombrados": renamed,
        "total": len(merged) + len(renamed)
    }

class LabelPayload(BaseModel):
    id: str
    name: Optional[str] = None
    color: Optional[str] = None

@app.post("/api/admin/labels/save")
async def api_save_label(payload: LabelPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    if not es_admin(request):
        raise HTTPException(status_code=403, detail="Solo administradores")
    from firebase_client import guardar_etiqueta_bd
    guardar_etiqueta_bd(payload.id, payload.name, payload.color)
    global global_labels
    global_labels = [l for l in global_labels if l.get("id") != payload.id]
    global_labels.append({"id": payload.id, "name": payload.name, "color": payload.color})
    return {"ok": True}

class GroupPayload(BaseModel):
    id: str
    name: str
    members: list[str]

@app.post("/api/admin/groups/save")
async def api_save_group(payload: GroupPayload, request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    global global_groups
    found = False
    for i, g in enumerate(global_groups):
        if g.get("id") == payload.id:
            global_groups[i] = payload.dict()
            found = True
            break
    if not found: global_groups.append(payload.dict())
    try:
        from firebase_client import guardar_grupo_bd
        guardar_grupo_bd(payload.dict())
    except: pass
    return {"ok": True}

@app.post("/api/admin/groups/delete")
async def api_delete_group(payload: GroupPayload, request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    global global_groups
    global_groups = [g for g in global_groups if g.get("id") != payload.id]
    try:
        from firebase_client import eliminar_grupo_bd
        eliminar_grupo_bd(payload.id)
    except: pass
    return {"ok": True}

@app.get("/api/admin/groups/list")
async def api_list_groups(request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    global global_groups
    if not global_groups:
        try: 
            from firebase_client import cargar_grupos_bd
            global_groups = cargar_grupos_bd()
        except: pass
    return {"groups": global_groups}

class ReorderPayload(BaseModel):
    order: list

@app.post("/api/admin/labels/reorder")
async def api_reorder_labels(payload: ReorderPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    if not es_admin(request):
        raise HTTPException(status_code=403, detail="Solo administradores")
        
    from firebase_client import reordenar_etiquetas_bd
    reordenar_etiquetas_bd(payload.order)
    
    # Update global memory
    global global_labels
    order_map = {lbl_id: idx for idx, lbl_id in enumerate(payload.order)}
    for lbl in global_labels:
        lbl["orden"] = order_map.get(lbl["id"], 999)
    global_labels.sort(key=lambda x: x.get("orden", 999))
    
    return {"ok": True}

@app.post("/api/admin/labels/delete")
async def api_delete_label(payload: LabelPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    if not es_admin(request):
        raise HTTPException(status_code=403, detail="Solo administradores")
    from firebase_client import eliminar_etiqueta_bd
    eliminar_etiqueta_bd(payload.id)
    global global_labels
    global_labels = [l for l in global_labels if l.get("id") != payload.id]
    
    # Quitar etiqueta de sesiones cargadas
    for k, s in sesiones.items():
        if "etiquetas" in s and payload.id in s["etiquetas"]:
            s["etiquetas"].remove(payload.id)
    return {"ok": True}

@app.get("/api/admin/labels/list")
async def api_list_labels(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    global global_labels
    if not global_labels:
        try:
            from firebase_client import cargar_etiquetas_bd
            global_labels = cargar_etiquetas_bd()
            print("🔄 Etiquetas recargadas dinámicamente desde Firebase.")
        except Exception as e:
            print(f"Error recargando etiquetas: {e}")
    return {"ok": True, "labels": global_labels}

class AssignLabelPayload(BaseModel):
    wa_id: str
    label_ids: list

@app.post("/api/admin/chats/labels")
async def api_assign_chat_labels(payload: AssignLabelPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    
    from firebase_client import cargar_sesion_chat, guardar_sesion_chat
    s = cargar_sesion_chat(payload.wa_id)
    if not s:
        s = sesiones.get(payload.wa_id)
        
    if s:
        s["etiquetas"] = payload.label_ids
        try:
            guardar_sesion_chat(payload.wa_id, s)
        except Exception as e:
            print(f"Error guardando etiquetas en BD: {e}")
            
        if payload.wa_id in sesiones:
            sesiones[payload.wa_id]["etiquetas"] = payload.label_ids
        return {"ok": True}
    return {"ok": False, "error": "Chat no existe"}

class ToggleLabelPayload(BaseModel):
    wa_id: str
    label_id: str
    action: str

@app.post("/api/admin/chats/labels/toggle")
async def api_toggle_chat_label(payload: ToggleLabelPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
        
    from firebase_client import cargar_sesion_chat, guardar_sesion_chat
    
    # 1. Intentar cargar desde Firestore
    s = cargar_sesion_chat(payload.wa_id)
    
    # 2. Si no existe en Firestore, intentar desde memoria (chat nuevo)
    if not s:
        s = sesiones.get(payload.wa_id)
        
    if s:
        current_labels = set(s.get("etiquetas", []))
        if payload.action == "add":
            current_labels.add(payload.label_id)
        elif payload.action == "rm":
            current_labels.discard(payload.label_id)
        elif payload.action == "toggle":
            if payload.label_id in current_labels:
                current_labels.discard(payload.label_id)
            else:
                current_labels.add(payload.label_id)
        
        s["etiquetas"] = list(current_labels)
        try:
            guardar_sesion_chat(payload.wa_id, s)
        except Exception as e:
            print(f"Error toggleando etiqueta en BD: {e}")
        
        if payload.wa_id in sesiones:
            sesiones[payload.wa_id]["etiquetas"] = list(current_labels)
            
        return {"ok": True}
        
    return {"ok": False, "error": "Chat no existe en memoria ni BD"}

class ChatActionPayload(BaseModel):
    wa_id: str
    action: str

@app.post("/api/admin/chat/action")
async def api_chat_action(payload: ChatActionPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
        
    from firebase_client import cargar_sesion_chat, guardar_sesion_chat, inicializar_firebase, guardar_grupo_bd, eliminar_grupo_bd
    wa_id = payload.wa_id
    action = payload.action
    global global_groups
    
    if wa_id.startswith("vg_"):
        found_g = next((g for g in global_groups if g.get("id") == wa_id), None)
        if not found_g and action != "delete": return {"ok": False, "error": "Grupo no existe"}
        
        if action == "archive":
            found_g["is_archived"] = not found_g.get("is_archived", False)
            try: guardar_grupo_bd(found_g)
            except: pass
            return {"ok": True, "state": found_g["is_archived"]}
        elif action == "pin":
            found_g["is_pinned"] = not found_g.get("is_pinned", False)
            try: guardar_grupo_bd(found_g)
            except: pass
            return {"ok": True, "state": found_g["is_pinned"]}
        elif action == "delete":
            global_groups = [g for g in global_groups if g.get("id") != wa_id]
            try: eliminar_grupo_bd(wa_id)
            except: pass
            return {"ok": True}
        return {"ok": True}
    
    s = cargar_sesion_chat(wa_id)
    if not s:
        s = sesiones.get(wa_id)
        
    if not s and action != "delete":
        return {"ok": False, "error": "Chat no existe"}
        
    if action == "archive":
        s["is_archived"] = not s.get("is_archived", False)
        if wa_id in sesiones: sesiones[wa_id] = s
        guardar_sesion_chat(wa_id, s)
        return {"ok": True, "state": s["is_archived"]}
        
    elif action == "pin":
        s["is_pinned"] = not s.get("is_pinned", False)
        if wa_id in sesiones: sesiones[wa_id] = s
        guardar_sesion_chat(wa_id, s)
        return {"ok": True, "state": s["is_pinned"]}
        
    elif action == "unread":
        s["unread_count"] = -1
        if wa_id in sesiones: sesiones[wa_id] = s
        guardar_sesion_chat(wa_id, s)
        return {"ok": True}
        
    elif action == "toggleBot":
        current_active = s.get("bot_activo", True)
        s["bot_activo"] = not current_active
        if not s["bot_activo"]:
            s["escalado_en"] = datetime.utcnow()
            s["motivo_escalacion"] = "Intervención manual"
        else:
            s["escalado_en"] = None
            s["motivo_escalacion"] = None
        if wa_id in sesiones: sesiones[wa_id] = s
        guardar_sesion_chat(wa_id, s)
        return {"ok": True, "state": s["bot_activo"]}
        
    elif action == "delete":
        if wa_id in sesiones:
            del sesiones[wa_id]
        if wa_id in mensajes_pendientes:
            del mensajes_pendientes[wa_id]
        try:
            db = inicializar_firebase()
            db.collection("chats_atc").document(wa_id).delete()
            print(f"🗑️ [BD] Chat {wa_id} eliminado exitosamente de Firebase.")
        except Exception as e: 
            print(f"[ERROR] [BD] Error eliminando {wa_id} de Firebase: {e}")
            pass
        return {"ok": True}
        
    return {"ok": False, "error": "Acción inválida"}






@app.get('/api/test_links')
async def api_test_links(text: str = 'Prueba con https://www.instagram.com'):
    import re
    texto_renderizado = text.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
    def linkify_text(match):
        if match.group(1): return match.group(1)
        url = match.group(2)
        trailing = ''
        while url and url[-1] in '.,!?)':
            trailing = url[-1] + trailing
            url = url[:-1]
        href = url if url.startswith('http') else 'http://' + url
        return f'<a href="{href}" target="_blank">{url}</a>{trailing}'
    texto_renderizado = re.sub(r'(<[^>]+>)|((?:https?://|www\.|wa\.me/)[^\s<>]+|[a-zA-Z0-9_-]+\.[a-zA-Z]{2,5}(?:/[^\s<>]*)?)', linkify_text, texto_renderizado)
    return {'original': text, 'resultado': texto_renderizado}

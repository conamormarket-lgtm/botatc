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

import os
from fastapi.staticfiles import StaticFiles
os.makedirs("static/stickers", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

@app.on_event("startup")
def startup_event():
    # ── Restaurar toda la memoria y stickers desde Firebase ──
    try:
        from firebase_client import cargar_todas_las_sesiones, cargar_stickers_de_bd
        # Restaurar sesiones (Inbox)
        sesiones_restauradas = cargar_todas_las_sesiones()
        for wa_id, s in sesiones_restauradas.items():
            sesiones[wa_id] = s
        print(f"✅ Se restauraron {len(sesiones_restauradas)} conversaciones en memoria desde Firebase.")
        
        # Restaurar Libreria de Stickers estatica
        import os
        os.makedirs("static/stickers", exist_ok=True)
        count_stickers = cargar_stickers_de_bd("static/stickers")
        print(f"✅ Se restauraron {count_stickers} stickers desde la DB al FileSystem efímero.")
        
        # Restaurar Etiquetas
        from firebase_client import cargar_etiquetas_bd
        global global_labels
        global_labels = cargar_etiquetas_bd()
        print(f"✅ Se restauraron {len(global_labels)} etiquetas globales.")
    except Exception as e:
        print(f"❌ Error al restaurar datos desde Firebase: {e}")

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

def obtener_o_crear_sesion(numero_wa: str) -> dict:
    """
    Retorna la sesión existente si está dentro del tiempo válido,
    la recupera de Firestore si el bot se reinició, o crea una nueva.
    """
    ahora = datetime.utcnow()
    sesion = sesiones.get(numero_wa)

    if not sesion:
        # 1. Intentar cargar desde Firebase si el servidor se reinició
        try:
            from firebase_client import cargar_sesion_chat
            sesion_db = cargar_sesion_chat(numero_wa)
            if sesion_db:
                sesiones[numero_wa] = sesion_db
                sesion = sesion_db
                print(f"  [☁️ Historial recuperado desde la nube para {numero_wa}]")
        except Exception as e:
            print(f"  [❌ Error al cargar historial de Firestore: {e}]")

    if sesion:
        pass # La sesión ya no expira nunca, como en un Inbox real

    if not sesion:
        sesiones[numero_wa] = {
            "historial":         [{"role": "system", "content": get_system_prompt()}],
            "datos_pedido":      None,
            "bot_activo":        True,
            "ultima_actividad":  ahora,
            "escalado_en":       None,
            "motivo_escalacion": None,
            "nombre_cliente":    "Cliente",
        }

    return sesiones[numero_wa]


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
            max_output_tokens=800,
            safety_settings=[
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            ]
        )
        
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=gemini_contents,
            config=config,
        )
        return response.text.strip()
    except Exception as e:
        import traceback
        with open("error_gemini.txt", "w") as f:
            f.write(traceback.format_exc())
        print(f"❌ Error Gemini: {e}")
        return "Disculpa, tuve un problema técnico. Intenta en un momento. 🙏"


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
        print("✅ Webhook de Meta verificado correctamente.")
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

        # Ignorar eventos que no sean mensajes (ej: estados de entrega)
        if "messages" not in changes:
            return {"status": "ok"}

        mensaje_data  = changes["messages"][0]
        mensaje_id    = mensaje_data.get("id", "")
        
        # Ignorar mensajes duplicados enviados repetidamente por el webhook de Meta
        if mensaje_id in mensajes_procesados_ids:
            return {"status": "ok"}
        mensajes_procesados_ids[mensaje_id] = True
        
        # Mantener solo los últimos 1000 IDs para evitar fugas sin vaciar el historial reciente
        if len(mensajes_procesados_ids) > 1000:
            oldest = next(iter(mensajes_procesados_ids))
            del mensajes_procesados_ids[oldest]
            
        numero_wa     = mensaje_data["from"]           # ej: "51945257117"
        tipo_mensaje  = mensaje_data.get("type", "")

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
            media_id = mensaje_data.get("image", {}).get("id", "")
            caption  = mensaje_data.get("image", {}).get("caption", "")
            texto_cliente = f"[imagen:{media_id}]" + (f" {caption}" if caption else "")
            background_tasks.add_task(cachear_media, media_id)
        elif tipo_mensaje in ["audio", "voice"]:
            # WhatsApp puede enviar audio (grabados) o voice (voice notes)
            media_id = mensaje_data.get(tipo_mensaje, {}).get("id", "")
            texto_cliente = f"[audio:{media_id}]"
            background_tasks.add_task(cachear_media, media_id)
        elif tipo_mensaje == "video":
            texto_cliente = "[🎥 Video]"
        elif tipo_mensaje == "document":
            filename = mensaje_data.get("document", {}).get("filename", "archivo")
            texto_cliente = f"[📎 Archivo: {filename}]"
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

    dict_msg = {"texto": texto_cliente, "id": mensaje_id}
    if numero_wa not in mensajes_pendientes:
        mensajes_pendientes[numero_wa] = [dict_msg]
        background_tasks.add_task(procesador_agregado, numero_wa, nombre)
    else:
        mensajes_pendientes[numero_wa].append(dict_msg)

    return {"status": "ok"}


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
    global BOT_GLOBAL_ACTIVO
    if not BOT_GLOBAL_ACTIVO:
        print(f"  [⏹ Bot APAGADO globalmente → silencio]")
        return None

    # ── Obtener/crear sesión ──────────────────────────────
    sesion = obtener_o_crear_sesion(numero_wa)
    sesion["ultima_actividad"] = datetime.utcnow()
    sesion["nombre_cliente"]   = nombre

    # 1) Guardar mensaje TEMPRANO para que SIEMPRE aparezca en el Inbox, sin duplicarse
    # Verificamos si no es exactamente el mismo último mensaje
    if not sesion["historial"] or sesion["historial"][-1].get("msg_id") != msg_id:
        sesion["historial"].append({"role": "user", "content": texto_cliente, "msg_id": msg_id})

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
                
        # Solo lo agregamos si no está ya como último mensaje (evitar duplicados lógicos)
        if not sesion["historial"] or sesion["historial"][-1].get("content") != texto_cliente:
            sesion["historial"].append({"role": "user", "content": texto_cliente})

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
                    sesion["historial"][0] = {"role": "system", "content": get_system_prompt(datos)}
                    print(f"  [🧪 TESTER: Pedido '{id_pedido}' cargado]")
                else:
                    msg = f"❌ No encontré ningún pedido con el ID '{texto_cliente.strip()}'. Inténtalo de nuevo (escribe solo el ID exacto)."
                    if not is_simulacion:
                        enviar_mensaje(numero_wa, msg)
                    return msg
            else:
                # Primera vez: pedir el ID de pedido
                sesion["esperando_pedido_tester"] = True
                msg = "🧪 *Modo prueba activado.*\n\nEscríbeme el ID del pedido que deseas probar (tal como aparece en Firebase):"
                sesion["historial"].append({"role": "assistant", "content": msg})
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
                print(f"  [✅ Pedidos encontrados: {ids} | Evitando Diseño]")
                
                sesion["datos_pedido"] = pedidos_no_diseno[0]  # Backward compatibility for inbox
                sesion["pedidos_multiples"] = pedidos_no_diseno
                
                sesion["historial"][0] = {
                    "role": "system",
                    "content": get_system_prompt(pedidos_no_diseno)
                }
            else:
                print(f"  [❓ Sin pedido registrado → silencio]")
                try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
                except: pass
                return None
    else:
        # Ya hay sesión con datos_pedido.
        estado_actual = sesion["datos_pedido"].get("estadoGeneral", "")
        if estado_actual in ESTADOS_DISEÑO:
            print(f"  [🎨 Pedido volvió a Diseño → silencio]")
            try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
            except: pass
            return None

    # ── Si el bot está pausado (modo humano) → guardar el msg y silenciar ───
    if not sesion["bot_activo"]:
        sesion["ultima_actividad"] = datetime.utcnow()
        print(f"  [👤 Bot pausado → mensaje guardado en historial, humano atiende]")
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
    # Reemplazamos el texto original (raw) con el normalizado para Gemini
    if sesion["historial"] and sesion["historial"][-1]["role"] == "user":
        sesion["historial"][-1]["content"] = texto_modelo
        
    historial_para_gemini = recortar_historial(sesion["historial"])
    print(f"  [🧠 Enviando {len(historial_para_gemini)} turnos a Gemini]")
    respuesta_bot = llamar_gemini(historial_para_gemini)

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
    sesion["historial"].append({"role": "assistant", "content": respuesta_final, "msg_id": wamid_out})

    
    try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
    except: pass
    
    return respuesta_final


# ─────────────────────────────────────────────
#  Panel de administración
# ─────────────────────────────────────────────



from fastapi import Response

VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
active_sessions = {}

def verificar_sesion(request: Request):
    token = request.cookies.get("session_token")
    return token in active_sessions

@app.get("/login", response_class=HTMLResponse)
async def login_get():
    return obtener_login_html()

@app.post("/login")
async def login_post(response: Response, username: str = Form(...), password: str = Form(...)):
    if username in VALID_USERS and VALID_USERS[username] == password:
        import uuid
        token = str(uuid.uuid4())
        active_sessions[token] = username
        resp = RedirectResponse(url="/inbox", status_code=303)
        resp.set_cookie(key="session_token", value=token, httponly=True, max_age=86400)
        return resp
    return HTMLResponse(obtener_login_html(error="Usuario o clave incorrectos."), status_code=401)

@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session_token")
    return resp

def obtener_login_html(error=""):
    err_html = f'<div class="error">{error}</div>' if error else ''
    return """
    <html><head><title>Acceso Restringido — IA-ATC</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;700&display=swap" rel="stylesheet">
    <style>
      :root {
          --primary-color: #3b82f6; --primary-hover: #2563eb;
          --bg-main: #0f172a; --accent-bg: rgba(30, 41, 59, 0.7);
          --accent-border: rgba(255, 255, 255, 0.1);
          --text-main: #f8fafc; --text-muted: #94a3b8;
      }
      *{box-sizing:border-box;margin:0;padding:0}
      body{font-family:'Inter',sans-serif;display:flex;justify-content:center;
           align-items:center;min-height:100vh;background-color:var(--bg-main);
           background-image: radial-gradient(circle at 50% -20%, #1e3a8a 0%, var(--bg-main) 70%);
           color:var(--text-main);-webkit-font-smoothing: antialiased;}
      .glass-modal{background:var(--accent-bg);padding:3rem 2.5rem;border-radius:24px;
            box-shadow:0 25px 50px -12px rgba(0,0,0,.5);width:90%;max-width:380px;
            backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
            border:1px solid var(--accent-border);text-align:center;}
      .logo{font-size:3rem;margin-bottom:1rem;display:inline-block;animation:float 3s ease-in-out infinite}
      @keyframes float { 0%, 100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
      h2{font-family:'Outfit',sans-serif;font-size:1.5rem;margin-bottom:.5rem;font-weight:700}
      p.subtitle{font-size:.9rem;color:var(--text-muted);margin-bottom:2rem}
      label{font-size:.85rem;color:var(--text-muted);font-weight:500;display:block;margin-bottom:.5rem;text-align:left}
      input{width:100%;padding:1rem 1.25rem;border:1px solid var(--accent-border);border-radius:12px;
            font-size:1rem;outline:none;transition:all .2s;background:rgba(15,23,42,0.6);color:white;
            margin-bottom:1.5rem;}
      input:focus{border-color:var(--primary-color);box-shadow:0 0 0 3px rgba(59,130,246,.2)}
      button{width:100%;padding:1rem;background:var(--primary-color);color:white;
             border:none;border-radius:12px;font-size:1rem;font-weight:600;cursor:pointer;
             transition:background .2s;font-family:'Inter',sans-serif;}
      button:hover{background:var(--primary-hover)}
      .error{color:#ef4444;font-size:0.85rem;margin-bottom:1.5rem;font-weight:500;background:rgba(239, 68, 68, 0.1);padding:0.5rem;border-radius:8px;}
    </style></head>
    <body><div class="glass-modal">
      <div class="logo">🤖</div>
      <h2>Identificación</h2>
      <p class="subtitle">Ingresa tus credenciales del sistema</p>
      __ERR_HTML__
      <form method="post" action="/login">
        <label>Usuario</label>
        <input type="text" name="username" placeholder="Tu usuario..." required autofocus>
        <label>Contraseña</label>
        <input type="password" name="password" placeholder="Ingresa tu clave secreta..." required>
        <button type="submit">Desbloquear el Sistema</button>
      </form>
    </div></body></html>
    """.replace("__ERR_HTML__", err_html)

@app.get("/settings", response_class=HTMLResponse)
async def settings_panel(request: Request):
    """Personalización de Agente y Base de Conocimiento."""
    if not verificar_sesion(request):
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
    
    return HTMLResponse(html)

@app.get("/api/media/{media_id}")
async def get_media_endpoint(media_id: str):
    from fastapi.responses import Response
    if media_id in media_cache:
        data, mime = media_cache[media_id]
        return Response(content=data, media_type=mime)
        
    try:
        from whatsapp_client import obtener_media_url, descargar_media
        url = await obtener_media_url(media_id)
        if url:
            data, mime = await descargar_media(url)
            if data:
                media_cache[media_id] = (data, mime)
                return Response(content=data, media_type=mime)
    except: pass
    return Response(content=b"", status_code=404)

@app.get("/api/quick-replies")
async def get_quick_replies(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import cargar_quick_replies_bd
    return cargar_quick_replies_bd()

@app.post("/api/quick-replies")
async def create_quick_reply(request: Request, data: dict):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import guardar_quick_reply_bd
    import uuid
    new_id = str(uuid.uuid4())
    guardar_quick_reply_bd(
        id_qr=new_id,
        titulo=data.get("title", ""),
        contenido=data.get("content", ""),
        categoria=data.get("category", "General"),
        tipo=data.get("type", "text")
    )
    return {"status": "ok", "id": new_id}

@app.delete("/api/quick-replies/{qr_id}")
async def delete_quick_reply(request: Request, qr_id: str):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import eliminar_quick_reply_bd
    eliminar_quick_reply_bd(qr_id)
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
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")

    with open("guia_respuestas.md", "w", encoding="utf-8") as f:
        f.write(guia_content)
        
    # Limpiamos caché del bot nativo para que levante los nuevos conocimientos
    import prompts
    prompts._GUIA_CACHE = ""

    return RedirectResponse(url="/settings?saved=true", status_code=303)

@app.post("/api/settings/upload_pdf")
async def upload_pdf(request: Request, pdf_file: UploadFile = File(...)):
    if not verificar_sesion(request):
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
    if not verificar_sesion(request):
        return RedirectResponse(url="/login", status_code=303)
        
    import os
    if filename.endswith(".pdf") and os.path.exists(filename):
        os.remove(filename)
        import prompts
        prompts._GUIA_CACHE = ""
        
    return RedirectResponse(url="/settings?deleted=true", status_code=303)

@app.post("/api/settings/toggle_proactive")
async def toggle_proactive(request: Request):
    if not verificar_sesion(request):
        return RedirectResponse(url="/login", status_code=303)
    
    import pedidos_observer
    pedidos_observer.NOTIFICACIONES_PROACTIVAS_ACTIVAS = not pedidos_observer.NOTIFICACIONES_PROACTIVAS_ACTIVAS
    
    return RedirectResponse(url="/settings", status_code=303)

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

    def tiempo_relativo(dt):
        diff = ahora - dt
        m = int(diff.total_seconds() / 60)
        if m < 1:   return "ahora"
        if m < 60:  return f"hace {m}m"
        return f"hace {m//60}h {m%60}m"

    def ultimo_msg(sesion):
        hist = [m for m in sesion.get("historial", []) if m["role"] != "system"]
        if not hist: return "—"
        return hist[-1]["content"][:60] + ("…" if len(hist[-1]["content"]) > 60 else "")

    # ── Tabla: Esperando humano ──────────────────────────
    filas_esc = ""
    for num, s in escalados:
        hace   = tiempo_relativo(s["escalado_en"])
        nombre = s.get("nombre_cliente", num)
        motivo = (s.get("motivo_escalacion") or "—")[:55]
        pedido = s.get("datos_pedido", {}).get("id", "—") if s.get("datos_pedido") else "—"
        
        filas_esc += f"""
        <tr>
          <td><div style="font-weight:600;color:var(--text-main)">{nombre}</div><div style="font-size:0.75rem;color:var(--text-muted)">+{num}</div></td>
          <td><span class="badge pedido">#{pedido}</span></td>
          <td style="color:var(--danger-color);font-weight:600">{hace}</td>
          <td><span style="font-size:0.85rem;color:var(--text-muted)">{motivo}</span></td>
          <td style="display:flex;gap:0.5rem;align-items:center;">
            <a href="/inbox/{num}" class="btn-action btn-outline">Ir a Inbox</a>
            <form method="post" action="/admin/reactivar/{num}" style="margin:0">
              <button type="submit" class="btn-action btn-primary">Reactivar IA</button>
            </form>
          </td>
        </tr>"""
    if not filas_esc:
        filas_esc = '<tr class="empty-row"><td colspan="5">Ningún chat está esperando atención manual. Todo fluye automatizado. ✅</td></tr>'

    # ── Tabla: Todas las sesiones ────────────────────────
    todas = sorted(sesiones.items(), key=lambda x: x[1]["ultima_actividad"], reverse=True)
    filas_all = ""
    for num, s in todas:
        inactivo_horas = (ahora - s["ultima_actividad"]).total_seconds() / 3600
        activo   = s.get("bot_activo", True)
            
        nombre   = s.get("nombre_cliente", num)
        pedido   = s.get("datos_pedido", {}).get("id", "—") if s.get("datos_pedido") else "—"
        ult_act  = tiempo_relativo(s["ultima_actividad"])
        preview  = ultimo_msg(s)
        
        badge = '<span class="badge active">IA Bot</span>' if activo else '<span class="badge danger">Humano</span>'
        
        filas_all += f"""
        <tr>
          <td><div style="font-weight:600;color:var(--text-main)">{nombre}</div><div style="font-size:0.75rem;color:var(--text-muted)">+{num}</div></td>
          <td><span class="badge pedido">#{pedido}</span></td>
          <td>{badge}</td>
          <td style="color:var(--text-muted);font-size:0.85rem">{ult_act}</td>
          <td style="max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--text-muted);font-size:0.85rem">{preview}</td>
          <td>
            <a href="/inbox/{num}" class="btn-action btn-outline">Espiar Chat</a>
          </td>
        </tr>"""
    if not filas_all:
        filas_all = '<tr class="empty-row"><td colspan="6">Sin sesiones activas recientes.</td></tr>'

    # Reemplazos
    html = html.replace("{pwd}", "")
    html = html.replace("{color_global}", "#10b981" if BOT_GLOBAL_ACTIVO else "#ef4444")
    html = html.replace("{class_btn_toggle}", "danger" if BOT_GLOBAL_ACTIVO else "")
    html = html.replace("{txt_btn_toggle}", "Apagar IA Global" if BOT_GLOBAL_ACTIVO else "Activar IA Global")
    html = html.replace("{total_sesiones}", str(total))
    html = html.replace("{bots_activos}", str(n_activos))
    html = html.replace("{humanos_requeridos}", str(n_escalados))
    html = html.replace("{filas_esperando_humano}", filas_esc)
    html = html.replace("{filas_todas}", filas_all)
    
    return HTMLResponse(html)


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
async def admin_upload_media(file: UploadFile = File(...)):
    """Sube una imagen directamente desde la interfaz Web a Meta Graph."""
    try:
        from whatsapp_client import subir_media
        content = await file.read()
        media_id = await subir_media(content, file.content_type, file.filename or "upload.png")
        
        if media_id:
            return {"ok": True, "media_id": media_id}
        
        return {"ok": False, "error": "No se pudo subir a Meta"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/api/admin/enviar_manual")
async def enviar_manual_endpoint(request: Request):
    """Recibe mensaje del panel web y lo despacha a WhatsApp nativamente."""
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    
    data = await request.json()
    wa_id = data.get("wa_id")
    texto = data.get("texto", "").strip()
    reply_to_wamid = data.get("reply_to_wamid")
    
    if not wa_id or wa_id not in sesiones or not texto:
        return {"ok": False}
        
    s = sesiones[wa_id]
    # No guardamos en historial todavía, hasta confirmar envío
    
    from whatsapp_client import enviar_mensaje, enviar_media
    import re
    
    async def process_and_send():
        from whatsapp_client import enviar_media, enviar_mensaje, subir_media
        partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\]|\[sticker-local:[^\]]+\])', texto)
        last_wamid = None
        exito_alguna_parte = False
        
        for p in partes:
            p = p.strip()
            if not p: continue
            
            match_sticker = re.match(r"^\[sticker:([^\]]+)\]$", p)
            match_img = re.match(r"^\[imagen:([^\]]+)\]$", p)
            match_sticker_local = re.match(r"^\[sticker-local:([^\]]+)\]$", p)
            
            w_id_current = None
            if match_sticker: 
                w_id_current = enviar_media(wa_id, "sticker", match_sticker.group(1), reply_to_wamid)
            elif match_img: 
                w_id_current = enviar_media(wa_id, "image", match_img.group(1), reply_to_wamid)
            elif match_sticker_local:
                filename = match_sticker_local.group(1)
                filepath = os.path.join("static", "stickers", filename)
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f: file_bytes = f.read()
                    mime = "image/webp" if filepath.endswith(".webp") else "image/png"
                    w_id_meta = await subir_media(file_bytes, mime, filename)
                    if w_id_meta:
                        tipo = "sticker" if mime == "image/webp" else "image"
                        w_id_current = enviar_media(wa_id, tipo, w_id_meta, reply_to_wamid)
            else: 
                w_id_current = enviar_mensaje(wa_id, p, reply_to_wamid)
            
            if w_id_current:
                last_wamid = w_id_current
                exito_alguna_parte = True
                
        return exito_alguna_parte, last_wamid

    # Wait for the API to process it synchronously from the user's perspective
    exito, msg_wamid = await process_and_send()
    
    if exito:
        s["historial"].append({"role": "assistant", "content": texto, "msg_id": msg_wamid})
        s["ultima_actividad"] = datetime.utcnow()
        print(f"  [👤 Humano -> {wa_id}]: {texto}")
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

@app.get("/api/media/{media_id}")
async def get_media_proxy(request: Request, media_id: str):
    """Proxy para obtener imágenes o stickers de WhatsApp sin exponer el token cliente."""
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
        
    from whatsapp_client import obtener_media_url, descargar_media
    url = await obtener_media_url(media_id)
    if not url:
        return Response(content=b"", status_code=404)
        
    contenido, mime_type = await descargar_media(url)
    if not contenido:
        return Response(content=b"", status_code=404)
        
    return Response(content=contenido, media_type=mime_type or "image/jpeg")


# ─────────────────────────────────────────────
#  Health check y Debug
# ─────────────────────────────────────────────

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
    for m in msgs:
        es_bot    = m["role"] == "assistant"
        clase     = "burbuja-bot" if es_bot else "burbuja-user"
        lado      = "bot-lado" if es_bot else "user-lado"
        remitente = "🤖 María" if es_bot else f"👤 {nombre}"
        texto     = m["content"].replace("\n", "<br>")
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

def renderizar_inbox(request: Request, wa_id: str = None, tab: str = "all", label_filter: str = None):
    if not verificar_sesion(request):
        return HTMLResponse(obtener_login_html(), status_code=401)

    import os
    if not os.path.exists("inbox.html"): return HTMLResponse("404: inbox.html no encontrado")
        
    with open("inbox.html", "r", encoding="utf-8") as f:
        html = f.read()

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
    todas = sorted(sesiones.items(), key=lambda x: x[1]["ultima_actividad"], reverse=True)
    lista_chats_html = ""
    
    # ------------------ Generador de Filtro de Etiquetas HTML ------------------
    active_label_obj = next((l for l in global_labels if l.get("id") == label_filter), None) if label_filter else None
    active_label_name = active_label_obj.get("name") if active_label_obj else "Filtro: Ninguno"
    if active_label_name.endswith("Ninguno"): active_label_name = "Filtrar Etiquetas: Desactivado"

    labels_filter_html = f"""
    <div style="position:relative; margin-top:1rem; text-align:left;">
        <button type="button" onclick="const m = document.getElementById('inboxFilterMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:var(--text-main); font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
            {active_label_name}
        </button>
        
        <div id="inboxFilterMenu" style="display:none; position:absolute; top:calc(100% + 0.5rem); left:0; width:100%; max-width:250px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:8px; box-shadow:0 8px 16px rgba(0,0,0,0.5); flex-direction:column; z-index:100; overflow:hidden;">
            <a href="/inbox?tab={tab}" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{'var(--primary-color)' if not label_filter else 'transparent'};">Todas (Sin filtro)</a>
    """
    
    for l in global_labels:
        lid = l.get("id")
        lnombre = l.get("name", "Etiqueta")
        lcolor = l.get("color", "#94a3b8")
        is_active = (label_filter == lid)
        bg = f"{lcolor}33" if is_active else "transparent"
        labels_filter_html += f"""
            <a href="/inbox?tab={tab}&label={lid}" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; gap:0.6rem; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{bg};">
                <span style="width:12px; height:12px; border-radius:50%; background:{lcolor};"></span> {lnombre}
            </a>
        """
        
    labels_filter_html += '</div></div>'
    
    for num, s in todas:
        inactivo_horas = (ahora - s["ultima_actividad"]).total_seconds() / 3600
        activo = s.get("bot_activo", True)
        
        # Filtro de Tab
        if tab == "human" and activo:
            continue
            
        session_tags = s.get("etiquetas", [])
        if session_tags is None: session_tags = []
        
        # Filtro de Etiqueta (Label)
        if label_filter and label_filter not in session_tags:
            continue

        nombre   = s.get("nombre_cliente", num)
        if not nombre: nombre = num
        preview  = ultimo_msg(s)
        time_str = tiempo_relativo(s["ultima_actividad"])
        
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
            
        lista_chats_html += f"""
        <a href="/inbox/{num}?tab={tab}" class="chat-row {active_class}">
            <div class="chat-row-header">
                <span class="chat-name">{nombre}</span>
                <span class="chat-time">{time_str}</span>
            </div>
            <div class="chat-preview">{preview}</div>
            <div class="chat-badges">{badge_html}</div>
            {tags_html}
        </a>"""

    if not lista_chats_html:
        lista_chats_html = '<div style="padding:2rem;text-align:center;color:var(--text-muted);font-size:0.9rem">No hay conversacioes que coincidan con estos filtros.</div>'

    # Procesar Panel Derecho (Chat Viewer)
    chat_viewer_html = ""
    chat_view_css = ""
    
    # Auto-inicializar chat nuevo si se manda un número válido (ej. desde el buscador UI)
    if wa_id and wa_id not in sesiones:
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

    if not wa_id or wa_id not in sesiones:
        chat_viewer_html = """
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <h3>Tu Inbox está vacío</h3>
            <p>Selecciona una conversación a la izquierda o navega por números nuevos.</p>
        </div>"""
    else:
        # Renderizar Chat Activo
        s = sesiones[wa_id]
        nombre_chat = s.get("nombre_cliente", wa_id)
        activo_chat = s.get("bot_activo", True)
        msgs = [m for m in s.get("historial", []) if m["role"] != "system"]
        
        import re
        burbujas = ""
        for m in msgs:
            es_bot = m["role"] == "assistant"
            clase  = "bubble-bot" if es_bot else "bubble-user"
            lado   = "lado-izq" if es_bot else "lado-der"
            texto  = m["content"].replace("\\n", "<br>")
            
            # --- Renderizar media_id si es [sticker:ID] o [imagen:ID] ---
            import re
            
            def reemplazar_archivos_inline(match):
                tipo = match.group(1)
                media_id = match.group(2)
                src_url = media_id if media_id.startswith("http") else f"/api/media/{media_id}"
                
                if tipo == "sticker":
                    return f"""<div style="text-align:center;"><img src="{src_url}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display:inline-block;" alt="Sticker {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/150x150?text=Sticker';"></div>"""
                elif tipo == "imagen":
                    return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: inline-block;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""
                elif tipo == "audio":
                    return f'<div style="text-align:center;"><audio controls src="{src_url}" style="max-width: 250px; height: 40px; outline: none; margin-bottom: 5px;"></audio></div>'
                return match.group(0)

            # Reemplazar todas las etiquetas multimedia incrustadas en el texto usando una función regex,
            # permitiendo que coexistan con texto (ej: "[sticker:123] | Hola")
            texto_renderizado = re.sub(r"\[(sticker|imagen|audio):([^\]]+)\]", reemplazar_archivos_inline, texto)
            
            # Limpiar posibles delimitadores huérfanos si quedó un texto como "<HTML> | PN" 
            texto_renderizado = texto_renderizado.replace("</div> | ", "</div><br>")
            
            # Formatear el indicador de respuesta nativa
            import re
            match = re.match(r"^\[\[REPLY\|(.*?)\]\](.*)$", texto_renderizado, flags=re.DOTALL)
            if match:
                texto_citado = match.group(1)
                texto_restante = match.group(2)
                html_reply = f'<div style="font-size:0.75rem; color:var(--text-muted); background:rgba(0,0,0,0.15); padding:0.35rem 0.6rem; border-radius:6px; margin-bottom:0.4rem; border-left:3px solid var(--primary-color); display:flex; flex-direction:column; max-width:100%; overflow:hidden;"><span style="font-weight:600;font-size:0.65rem;margin-bottom:0.1rem;opacity:0.8;">Respondió a:</span><span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{texto_citado}</span></div>'
                texto_renderizado = html_reply + texto_restante
                
            wamid = m.get("msg_id", "")
            wamid_attr = f' data-wamid="{wamid}"' if wamid else ""
            burbujas += f'<div class="bubble {clase} {lado}"{wamid_attr} title="Click derecho (PC) o mantener presionado (Móvil) para opciones">{texto_renderizado}</div>'
            
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
                  <button type="submit" style="background:white;color:var(--danger-color);border:none;padding:0.3rem 0.8rem;border-radius:6px;font-weight:700;cursor:pointer;transition:transform 0.2s;">✅ Reactivar Bot</button>
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
        if activo_chat:
            chat_box = """
            <div style="opacity:0.6;font-size:0.85rem;color:var(--text-muted);display:flex;align-items:center;justify-content:center;padding:0.5rem;">
                El Bot IA está controlando este chat. Pausa al bot para intervenir.
            </div>"""
        else:
            chat_box = f"""
            <div id="replyPreviewContainer" style="display:none; align-items:center; justify-content:space-between; background:var(--accent-bg); padding: 0.5rem 1rem; border-left: 3px solid var(--primary-color); font-size: 0.85rem; color: var(--text-muted); border-radius: 8px 8px 0 0; margin-bottom: -0.5rem; position: relative;">
                <span style="font-family:var(--font-main);">Respondiendo a: <span id="replyPreviewTxt" style="color:var(--text-main);font-weight:600;">...</span></span>
                <button type="button" onclick="document.getElementById('replyPreviewContainer').style.display='none'; document.getElementById('replyToWamid').value='';" style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:1.1rem;padding:0;">×</button>
            </div>
            
            <form onsubmit="window.enviarMensajeManual(event, '{wa_id}')" style="display:flex; gap:0.5rem; width:100%; margin:0; position:relative; align-items:center;">
                <input type="hidden" id="replyToWamid" value="">
                
                <div style="position:relative; display:flex; gap:0.5rem;">
                    <!-- Emoji Picker Button -->
                    <button type="button" onclick="const m = document.getElementById('emojiMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:var(--bg-main); border:1px solid var(--accent-border); border-radius:50%; width:44px; height:44px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:background 0.2s;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='var(--bg-main)'" title="Emojis">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>
                    </button>
                    <!-- Menú Flotante de Emojis -->
                    <div id="emojiMenu" style="display:none; position:absolute; bottom:55px; left:0; z-index:1000; background:transparent; border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.15);">
                        <emoji-picker class="light"></emoji-picker>
                    </div>

                    <!-- Botón Clip (Adjuntos) -->
                    <button type="button" onclick="const m = document.getElementById('attachMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:var(--bg-main); border:1px solid var(--accent-border); border-radius:50%; width:44px; height:44px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:background 0.2s;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='var(--bg-main)'" title="Adjuntar">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                    </button>
                    <!-- Menú Flotante de Adjuntos -->
                    <div id="attachMenu" style="display:none; position:absolute; bottom:calc(100% + 0.8rem); left:0; width:190px; background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.5); padding:0.5rem; flex-direction:column; gap:0.2rem; z-index:100;">
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'imagen'); document.getElementById('hiddenFileInput').accept='image/*'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg> Subir Imagen
                        </button>
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; toggleStickersMenu();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg> Stickers
                        </button>
                    </div>

                    <!-- Botón Plantillas -->
                    <button type="button" onclick="const m = document.getElementById('templateMenu'); m.style.display = m.style.display==='none'?'flex':'none'; if(m.style.display==='flex') cargarPlantillas();" style="background:var(--bg-main); border:1px solid var(--accent-border); border-radius:50%; width:44px; height:44px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:background 0.2s;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='var(--bg-main)'" title="Plantillas (24h)">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                    </button>
                    <!-- Botón Quick Replies -->
                    <button type="button" onclick="const side = document.getElementById('rightSidebar'); side.style.display = side.style.display==='none'?'flex':'none'; if(side.style.display==='flex') cargarQuickReplies();" style="background:var(--bg-main); border:1px solid var(--accent-border); border-radius:50%; width:44px; height:44px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:background 0.2s;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='var(--bg-main)'" title="Respuestas Rápidas (/)">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M13 2v7h7"/><circle cx="10" cy="14" r="3"/><line x1="12" y1="16" x2="15" y2="19"/></svg>
                    </button>
                </div>

                <input type="text" id="manualMsgInput" placeholder="Escribe un mensaje... (/)" style="flex:1;padding:0.8rem 1rem;border-radius:12px;border:1px solid var(--accent-border);background:var(--bg-main);color:var(--text-main);outline:none;font-size:0.95rem;font-family:var(--font-main);" autocomplete="off" required oninput="checkQuickReplyTrigger(this)">
                <button type="submit" style="background:var(--primary-color);color:white;border:none;border-radius:12px;padding:0 1.5rem;height:44px;font-weight:600;font-size:0.95rem;cursor:pointer;transition:background 0.2s;">Enviar</button>
            </form>
            
            <script>
            let quickRepliesCache = [];
            async function cargarQuickReplies() {{
                const list = document.getElementById("quickRepliesList");
                if(!list) return;
                try {{
                    const res = await fetch("/api/quick-replies");
                    const data = await res.json();
                    quickRepliesCache = data;
                    renderQuickReplies(data);
                }} catch(e) {{
                    list.innerHTML = `<div style="font-size:0.8rem; color:red; padding:0.5rem; text-align:center;">Error al cargar</div>`;
                }}
            }}
            function renderQuickReplies(data) {{
                const list = document.getElementById("quickRepliesList");
                if(!list) return;
                if(data.length === 0) {{
                    list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:1rem; text-align:center; height:100%; display:flex; align-items:center; justify-content:center;">Sin respuestas rápidas en el sistema.</div>`;
                    return;
                }}
                list.innerHTML = "";
                data.forEach(qr => {{
                    const container = document.createElement("div");
                    container.style.cssText = "display:flex; flex-direction:column; background:var(--accent-bg); padding:0.75rem; border-radius:8px; border:1px solid var(--accent-border); transition:border-color 0.15s; position:relative;";
                    container.onmouseover = function() {{this.style.borderColor='var(--primary-color)';}};
                    container.onmouseout = function() {{this.style.borderColor='var(--accent-border)';}};
                    
                    const btn = document.createElement("button");
                    btn.type = "button";
                    btn.style.cssText = "background:none; border:none; text-align:left; cursor:pointer; color:var(--text-main); width:100%; display:flex; flex-direction:column;";
                    
                    const headerRow = document.createElement("div");
                    headerRow.style.cssText = "display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:0.2rem;";
                    
                    const title = document.createElement("strong");
                    title.innerText = qr.title || qr.category;
                    title.style.fontSize = "0.9rem";
                    
                    const catBadge = document.createElement("span");
                    catBadge.innerText = (qr.category && qr.category!==qr.title) ? qr.category : "";
                    catBadge.style.cssText = "font-size:0.65rem; background:rgba(255,255,255,0.1); padding:0.1rem 0.4rem; border-radius:4px;";
                    
                    headerRow.appendChild(title);
                    if(catBadge.innerText) headerRow.appendChild(catBadge);
                    
                    const prev = document.createElement("span");
                    prev.style.cssText = "font-size:0.8rem; color:var(--text-muted); display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; line-height:1.4;";
                    prev.innerText = qr.content;
                    
                    btn.onclick = () => aplicarQuickReply(qr.content);
                    btn.appendChild(headerRow);
                    btn.appendChild(prev);
                    
                    const delBtn = document.createElement("button");
                    delBtn.innerHTML = "×";
                    delBtn.title = "Eliminar";
                    delBtn.style.cssText = "position:absolute; top:0.5rem; right:0.5rem; background:rgba(0,0,0,0.3); border:none; color:#ef4444; border-radius:50%; width:20px; height:20px; display:flex; justify-content:center; align-items:center; cursor:pointer; opacity:0; transition:opacity 0.2s;";
                    container.onmouseenter = () => delBtn.style.opacity = "1";
                    container.onmouseleave = () => delBtn.style.opacity = "0";
                    
                    delBtn.onclick = (e) => {{
                        e.stopPropagation();
                        eliminarQR(qr.id);
                    }};
                    
                    container.appendChild(btn);
                    container.appendChild(delBtn);
                    list.appendChild(container);
                }});
            }}
            function filtrarQuickReplies(val) {{
                const valLower = val.toLowerCase();
                const filt = quickRepliesCache.filter(q => q.title?.toLowerCase().includes(valLower) || q.content?.toLowerCase().includes(valLower));
                renderQuickReplies(filt);
            }}
            function aplicarQuickReply(text) {{
                let nombreCliente = "{nombre_chat}";
                let finalMsg = text.replace(/#nombre/gi, nombreCliente);
                const input = document.getElementById("manualMsgInput");
                if(input) {{
                    const cursorPos = input.selectionStart;
                    const textBefore = input.value.substring(0, cursorPos);
                    const textAfter  = input.value.substring(cursorPos, input.value.length);
                    const slashMatch = textBefore.match(/(?:^|\\s)\/$/); 
                    
                    if (slashMatch) {{
                        input.value = textBefore.substring(0, textBefore.length - 1) + finalMsg + textAfter;
                    }} else {{
                        input.value += finalMsg;
                    }}
                    input.focus();
                    document.getElementById('rightSidebar').style.display = 'none';
                }}
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
            
            function abrirModalCrearQR() {{
                const m = document.getElementById('qrCreateModal');
                if(m) {{
                    document.getElementById('newQrTitle').value = '';
                    document.getElementById('newQrContent').value = '';
                    document.getElementById('newQrCat').value = 'General';
                    m.style.display = 'flex';
                    setTimeout(()=> document.getElementById('newQrTitle').focus(), 50);
                }}
            }}
            
            function insertarVariableQR(variable) {{
                const ta = document.getElementById('newQrContent');
                if(!ta) return;
                const pos = ta.selectionStart;
                const txt = ta.value;
                ta.value = txt.slice(0, pos) + variable + txt.slice(ta.selectionEnd);
                ta.selectionStart = ta.selectionEnd = pos + variable.length;
                ta.focus();
            }}

            async function guardarNuevoQR() {{
                const title = document.getElementById('newQrTitle').value.trim();
                const content = document.getElementById('newQrContent').value.trim();
                const cat = document.getElementById('newQrCat').value.trim() || "General";
                
                if(!title || !content) return alert("Se requiere Título y Mensaje para continuar.");
                
                const id_qr = "qr_" + Date.now();
                try {{
                    const res = await fetch("/api/quick-replies", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ id: id_qr, title: title, content: content, category: cat, type: "text" }})
                    }});
                    const d = await res.json();
                    if(d.ok || res.ok) {{
                        document.getElementById('qrCreateModal').style.display = 'none';
                        cargarQuickReplies();
                    }} else {{
                        alert("Hubo un error guardando.");
                    }}
                }} catch(e) {{
                    alert("Error enviando red");
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
            """

        session_tags = s.get("etiquetas", [])
        if session_tags is None: session_tags = []
        tags_bar = ""
        for tid in session_tags:
            lbl = next((l for l in global_labels if l.get("id") == tid), None)
            if lbl:
                col = lbl.get("color", "#94a3b8")
                nm = lbl.get("name", "Etiqueta")
                tags_bar += f'<span style="background:{col}22; color:{col}; font-size:0.65rem; padding:0.15rem 0.4rem; border-radius:4px; font-weight:600; border: 1px solid {col}44;">{nm}</span>'

        chat_viewer_html = f"""
        <div style="display:flex; flex-direction:row; height:100%; width:100%;">
            <!-- START CHAT MAIN COLUMN -->
            <div style="flex:1; display:flex; flex-direction:column; min-width:0; background:var(--bg-main);">
                {status_bar}
                <div style="padding:1.5rem;border-bottom:1px solid var(--accent-border);display:flex;align-items:center;background:var(--bg-main);">
                    <a href="/inbox?tab={tab}" class="btn-responsive-back" title="Volver a la lista">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                    </a>
                    <div style="width:40px;height:40px;border-radius:50%;background:var(--primary-color);color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;margin-right:1rem;font-size:1.2rem;flex-shrink:0">{{nombre_chat[0].upper()}}</div>
                    <div style="min-width:0; flex:1;">
                        <h3 style="margin:0;font-size:1.1rem;font-family:var(--font-heading);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:0.5rem;">
                            {{nombre_chat}} {{tags_bar}}
                        </h3>
                        <small style="color:var(--text-muted)">+{{wa_id}}</small>
                    </div>
                    <!-- Botón de gestionar etiquetas -->
                    <div style="position:relative;">
                        <button type="button" onclick="const m = document.getElementById('chatLabelMenu'); m.style.display = m.style.display==='none'?'flex':'none'; if(m.style.display==='flex') cargarChatLabels();" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem; padding:0.5rem; border-radius:50%; transition:background 0.2s;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='none'" title="Etiquetas del Chat">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                        </button>
                        <div id="chatLabelMenu" style="display:none; position:absolute; top:calc(100% + 0.5rem); right:0; width:220px; background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.5); padding:0.5rem; flex-direction:column; gap:0.4rem; z-index:100;">
                            <div style="font-weight:600; font-size:0.8rem; color:var(--text-muted); padding:0.3rem 0.5rem; border-bottom:1px solid var(--accent-border); display:flex; justify-content:space-between; align-items:center;">
                                Etiquetas 
                                <button type="button" onclick="crearGlobalLabel()" style="background:none; border:none; color:var(--primary-color); cursor:pointer; font-size:1rem; padding:0;" title="Nueva Etiqueta Global">+</button>
                            </div>
                            <div id="chatLabelList" style="display:flex; flex-direction:column; gap:0.2rem; max-height:220px; overflow-y:auto;">
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="flex:1;overflow-y:auto;padding:1.5rem;display:flex;flex-direction:column;gap:0.5rem;" id="chatScroll">
                    {burbujas}
                </div>
                
                <div id="stickersDrawer" style="display:none; padding:1.5rem; background:var(--bg-main); border-top:1px solid var(--accent-border); height:220px; overflow-y:auto; overflow-x:hidden;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                        <span style="font-weight:600; color:var(--text-main);">Librería de Stickers Locales</span>
                    </div>
                    <div id="stickersGrid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 1rem; justify-items: center;"></div>
                </div>
                
                <div style="padding:1rem 1.5rem;border-top:1px solid var(--accent-border);background:var(--accent-bg);">
                    {chat_box}
                </div>
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

                <!-- Hidden section / Sub-panel for Creating QR -->
                <div id="qrCreateModal" style="display:none; position:absolute; inset:0; background:var(--bg-main); flex-direction:column; z-index:10; border-left:1px solid var(--accent-border);">
                    <div style="padding:1.5rem; border-bottom:1px solid var(--accent-border); display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="font-family:var(--font-heading); font-size:1.1rem; flex:1; margin:0;">Crear Respuesta</h3>
                        <button onclick="document.getElementById('qrCreateModal').style.display='none'" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem;">×</button>
                    </div>
                    <div style="padding:1.5rem; display:flex; flex-direction:column; gap:1.2rem; flex:1; overflow-y:auto;">
                        <div>
                            <label style="display:block; font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem; font-weight:600;">Atajo / Título</label>
                            <input type="text" id="newQrTitle" placeholder="ej: saludo" style="width:100%; padding:0.6rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.9rem;">
                        </div>
                        <div>
                            <label style="display:block; font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem; font-weight:600;">Mensaje</label>
                            <textarea id="newQrContent" rows="6" placeholder="Escribe el bloque de texto..." style="width:100%; padding:0.6rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.9rem; resize:vertical;"></textarea>
                            <div style="margin-top:0.5rem; display:flex; gap:0.5rem;">
                                <button onclick="insertarVariableQR('#nombre')" style="background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); color:var(--primary-color); font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:4px; font-weight:600; cursor:pointer;" title="Inserta el nombre del contacto">+#nombre</button>
                            </div>
                        </div>
                        <div>
                            <label style="display:block; font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem; font-weight:600;">Categoría (Opcional)</label>
                            <input type="text" id="newQrCat" placeholder="General" style="width:100%; padding:0.6rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.9rem;">
                        </div>
                    </div>
                    <div style="padding:1.5rem; border-top:1px solid var(--accent-border);">
                        <button onclick="guardarNuevoQR()" style="width:100%; background:var(--primary-color); color:white; border:none; padding:0.8rem; border-radius:6px; font-weight:600; cursor:pointer; font-size:0.95rem;">Guardar Respuesta</button>
                    </div>
                </div>
            </div>
            <!-- END RIGHT SIDEBAR -->
        </div>
        <script>
            var c = document.getElementById('chatScroll');
            if(c) c.scrollTop = c.scrollHeight;
        </script>
        """
        
        chat_view_css = """
        .bubble { max-width:80%; padding:0.8rem 1rem; border-radius:12px; font-size:0.95rem; line-height:1.4; position:relative; }
        .lado-izq { align-self:flex-start; }
        .lado-der { align-self:flex-end; }
        .bubble-bot { background:var(--accent-bg); color:var(--text-main); border-bottom-left-radius:4px; border:1px solid var(--accent-border); }
        .bubble-user { background:var(--primary-color); color:#ffffff; border-bottom-right-radius:4px; }
        """

    # Reemplazos finales en la plantilla
    es_chat_valido = bool(wa_id and wa_id in sesiones)
    html = html.replace("{body_class}", "view-chat" if es_chat_valido else "view-list")
    html = html.replace("{tab_all_active}", "active" if tab != "human" else "")
    html = html.replace("{tab_human_active}", "active" if tab == "human" else "")
    html = html.replace("{lista_chats_html}", lista_chats_html)
    html = html.replace("{labels_filter_html}", labels_filter_html)
    html = html.replace("{chat_viewer_html}", chat_viewer_html)
    html = html.replace("{chat_view_css}", chat_view_css)
    html = html.replace("{color_global}", "#10b981" if BOT_GLOBAL_ACTIVO else "#ef4444")
    
    return HTMLResponse(html)

@app.get("/inbox", response_class=HTMLResponse)
async def inbox_main(request: Request, tab: str = "all", label: str = None):
    return renderizar_inbox(request, None, tab, label)

from typing import List

@app.post("/api/admin/stickers/upload")
async def upload_stickers(files: List[UploadFile] = File(...)):
    """Recibe múltiples archivos webp/png, los guarda en disco ephemeral y sincroniza a Firestore."""
    try:
        import os
        from firebase_client import guardar_sticker_en_bd
        os.makedirs("static/stickers", exist_ok=True)
        count = 0
        for file in files:
            if file.filename.endswith(".webp") or file.filename.endswith(".png"):
                # Extraemos solo el nombre del archivo, ignorando subcarpetas
                basename = os.path.basename(file.filename)
                filepath = os.path.join("static", "stickers", basename)
                content = await file.read()
                
                # Guardar local efímero (para el render estático actual)
                with open(filepath, "wb") as f:
                    f.write(content)
                
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
    
    import os
    from firebase_client import guardar_sticker_en_bd
    basename = f"fav_{media_id}.webp"
    
    os.makedirs("static/stickers", exist_ok=True)
    filepath = os.path.join("static", "stickers", basename)
    with open(filepath, "wb") as f:
        f.write(contenido)
        
    guardar_sticker_en_bd(basename, contenido)
    return {"ok": True, "filename": basename}


@app.get("/api/stickers")
def get_stickers():
    """Retorna la lista de stickers webp disponibles localmente."""
    try:
        if not os.path.exists("static/stickers"): return {"ok": True, "stickers": []}
        files = os.listdir("static/stickers")
        stickers = [f for f in files if f.endswith(".webp") or f.endswith(".png")]
        return {"ok": True, "stickers": stickers}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/inbox/{wa_id}", response_class=HTMLResponse)
async def inbox_chat(request: Request, wa_id: str, tab: str = "all", label: str = None):
    return renderizar_inbox(request, wa_id, tab, label)

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
            "pedido_id": s.get("datos_pedido", {}).get("id") if s.get("datos_pedido") else None,
            "estado_pedido": s.get("datos_pedido", {}).get("estadoGeneral") if s.get("datos_pedido") else None,
            "mensajes": historial_resumido,
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
                addMessage("<span style='color:red'>⚠️ Error de conexión</span>", 'msg-bot');
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

@app.post("/api/admin/templates/save")
async def api_save_template(payload: TemplatePayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import guardar_plantilla_bd
    guardar_plantilla_bd(payload.name, payload.language)
    return {"ok": True}

@app.post("/api/admin/templates/delete")
async def api_delete_template(payload: TemplatePayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import eliminar_plantilla_bd
    eliminar_plantilla_bd(payload.name)
    return {"ok": True}

@app.get("/api/admin/templates/list")
async def api_list_templates(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import cargar_plantillas_bd
    plantillas = cargar_plantillas_bd()
    return {"ok": True, "plantillas": plantillas}

class EnviarPlantillaPayload(BaseModel):
    wa_id: str
    template_name: str
    language_code: str = "es"

@app.post("/api/admin/enviar_plantilla")
async def api_enviar_plantilla(payload: EnviarPlantillaPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
        
    from whatsapp_client import enviar_plantilla
    wamid = await enviar_plantilla(payload.wa_id, payload.template_name, payload.language_code)
    
    if wamid:
        # Registrar el envío en el historial del dashboard
        from firebase_client import cargar_sesion_chat, guardar_sesion_chat
        s = cargar_sesion_chat(payload.wa_id)
        if s:
            if "historial" not in s: s["historial"] = []
            s["historial"].append({"role": "assistant", "content": f"[Plantilla enviada: {payload.template_name}]", "msg_id": wamid})
            from datetime import datetime
            s["ultima_actividad"] = datetime.utcnow()
            guardar_sesion_chat(payload.wa_id, s)
        return {"ok": True, "wamid": wamid}
    return {"ok": False, "error": "No se pudo enviar (Verifica que el WABA ID sea el correcto o Meta la rechazó)."}


# ============================================================
#  API DE GESTOR DE ETIQUETAS Y ASIGNACIONES
# ============================================================

from typing import Optional

class LabelPayload(BaseModel):
    id: str
    name: Optional[str] = None
    color: Optional[str] = None

@app.post("/api/admin/labels/save")
async def api_save_label(payload: LabelPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    from firebase_client import guardar_etiqueta_bd
    guardar_etiqueta_bd(payload.id, payload.name, payload.color)
    global global_labels
    global_labels = [l for l in global_labels if l.get("id") != payload.id]
    global_labels.append({"id": payload.id, "name": payload.name, "color": payload.color})
    return {"ok": True}

@app.post("/api/admin/labels/delete")
async def api_delete_label(payload: LabelPayload, request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
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
    if s:
        s["etiquetas"] = payload.label_ids
        guardar_sesion_chat(payload.wa_id, s)
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
        guardar_sesion_chat(payload.wa_id, s)
        
        if payload.wa_id in sesiones:
            sesiones[payload.wa_id]["etiquetas"] = list(current_labels)
            
        return {"ok": True}
        
    return {"ok": False, "error": "Chat no existe en memoria ni BD"}

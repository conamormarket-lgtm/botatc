# ============================================================
#  bot_atc.py — Bot conversacional con extracción automática
#               de identificadores (teléfono / N° pedido)
#
#  FLUJO:
#    1. El bot saluda y conversa naturalmente
#    2. El cliente escribe lo que quiera (frases libres)
#    3. El sistema escanea cada mensaje con regex buscando:
#       - Teléfonos peruanos (9 dígitos empezando en 9)
#       - Números de pedido (4-6 dígitos)
#    4. Si encuentra un candidato → consulta Firebase silenciosamente
#    5. Si halla el pedido → actualiza el contexto del bot con datos reales
#    6. El bot responde con información precisa sin que el cliente note nada
# ============================================================
import re
from openai import OpenAI

from config import (
    LM_STUDIO_BASE_URL, LM_STUDIO_API_KEY, LM_STUDIO_MODEL,
    TEMPERATURE, MAX_HISTORIAL_TURNOS
)
from prompts import get_system_prompt, MENSAJE_BIENVENIDA
from firebase_client import buscar_pedido_por_telefono, buscar_pedido_por_id


# ─────────────────────────────────────────────
#  Cliente LM Studio
# ─────────────────────────────────────────────
llm = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)


# ─────────────────────────────────────────────
#  Extracción de identificadores con regex
# ─────────────────────────────────────────────

# Teléfono peruano: empieza en 9, tiene 9 dígitos
# Ejemplos: 945257117 | 945 257 117 | 945-257-117
REGEX_TELEFONO = re.compile(r'\b9\d{2}[\s\-]?\d{3}[\s\-]?\d{3}\b')

# Número de pedido: 4 a 6 dígitos seguidos (ej: 5452, 10234)
# Excluir si va justo antes/después de más dígitos para no confundir con teléfonos
REGEX_PEDIDO = re.compile(r'(?<!\d)(\d{4,6})(?!\d)')


def extraer_telefono(texto: str) -> str | None:
    """
    Extrae un teléfono peruano de 9 dígitos del texto.
    Valida que sean EXACTAMENTE 9 dígitos (ni 8 ni 10).
    Así evita tomar los primeros 9 de un número de 10 dígitos.
    """
    match = REGEX_TELEFONO.search(texto)
    if match:
        solo_digitos = re.sub(r'[\s\-]', '', match.group())
        if len(solo_digitos) == 9:   # exactamente 9 dígitos
            return solo_digitos
    return None


def extraer_id_pedido(texto: str) -> str | None:
    """
    Extrae el primer número que podría ser un ID de pedido (4-6 dígitos).
    Descarta los que empiezan en 9 (probablemente son teléfonos).
    """
    for match in REGEX_PEDIDO.finditer(texto):
        candidato = match.group()
        if not candidato.startswith('9') or len(candidato) < 9:
            return candidato
    return None


def intentar_obtener_pedido(mensaje: str) -> dict | None:
    """
    Analiza el mensaje del cliente buscando un teléfono o ID de pedido.
    Si encuentra uno, consulta Firebase.
    Prioridad: teléfono > número de pedido.
    """
    # 1) Buscar por teléfono
    tel = extraer_telefono(mensaje)
    if tel:
        print(f"  [🔍 Detectado teléfono: {tel} → consultando Firebase...]")
        datos = buscar_pedido_por_telefono(tel)
        if datos:
            return datos

    # 2) Buscar por número de pedido
    id_pedido = extraer_id_pedido(mensaje)
    if id_pedido:
        print(f"  [🔍 Detectado N° pedido: {id_pedido} → consultando Firebase...]")
        datos = buscar_pedido_por_id(id_pedido)
        if datos:
            return datos

    return None


# ─────────────────────────────────────────────
#  Normalización de español informal / chat
# ─────────────────────────────────────────────

# Abreviaciones ordenadas de más larga a más corta para evitar reemplazos parciales
_ABREVIACIONES = [
    # Palabras completas (word boundary)
    (r'\bxq\b',     'porque'),
    (r'\bpq\b',     'porque'),
    (r'\bporq\b',   'porque'),
    (r'\bxke\b',    'porque'),
    (r'\btmb\b',    'también'),
    (r'\btb\b',     'también'),
    (r'\bpls\b',    'por favor'),
    (r'\bplz\b',    'por favor'),
    (r'\bporfas\b', 'por favor'),
    (r'\bporfa\b',  'por favor'),
    (r'\bgrax\b',   'gracias'),
    (r'\bgrcs\b',   'gracias'),
    (r'\bkiero\b',  'quiero'),
    (r'\bkieres\b', 'quieres'),
    (r'\bkien\b',   'quién'),
    (r'\bke\b',     'que'),
    (r'\bq\b',      'que'),
    (r'\bk\b',      'que'),
    (r'\bxfa\b',    'por favor'),
    (r'\bx\b',      'por'),
    (r'\bd\b',      'de'),
    (r'\bm\b',      'me'),
    (r'\bbn\b',     'bien'),
    (r'\bbien\b',   'bien'),
    (r'\bsta\b',    'está'),
    (r'\bstas\b',   'están'),
    (r'\btdo\b',    'todo'),
    (r'\btda\b',    'toda'),
    (r'\bnd\b',     'nada'),
    (r'\bslds\b',   'saludos'),
    (r'\bmsj\b',    'mensaje'),
    (r'\bpdo\b',    'pedido'),
    (r'\bpgue\b',   'pagué'),
    (r'\bpague\b',  'pagué'),
]

# Compilar una vez al cargar el módulo
_ABREV_COMPILADAS = [(re.compile(pat, re.IGNORECASE), reemplazo)
                     for pat, reemplazo in _ABREVIACIONES]


def normalizar_texto(mensaje: str) -> str:
    """
    Expande abreviaciones de chat informal peruano al español completo.
    Ejemplo: "q paso con el pedido q pague" →
             "que paso con el pedido que pagué"
    El modelo entiende mucho mejor el texto normalizado.
    """
    resultado = mensaje
    for patron, reemplazo in _ABREV_COMPILADAS:
        resultado = patron.sub(reemplazo, resultado)
    return resultado



# Palabras que en contexto peruano indican que "cancelar" = pagar/saldar
_REGEX_CANCELAR = re.compile(r'\bcancela[r]?\b', re.IGNORECASE)
_REGEX_CONTEXTO_PAGO = re.compile(
    r'\b(monto|pago|total|deuda|saldo|completo|toda|todo|cuota|adelanto|restante|pendiente|precio|costo)\b',
    re.IGNORECASE
)

def preprocesar_mensaje(mensaje: str) -> str:
    """
    En Perú, 'cancelar el monto/pago/deuda' significa PAGAR, no anular.
    Si el modelo ve 'cancelar' con contexto de pago, agrega una aclaración
    inline para que no lo confunda con 'revocar/anular el pedido'.
    Esta función actúa ANTES de enviar el mensaje al modelo.
    """
    if _REGEX_CANCELAR.search(mensaje) and _REGEX_CONTEXTO_PAGO.search(mensaje):
        return (
            f"{mensaje}"
            f"\n[ACLARACIÓN AUTOMÁTICA: en este contexto, 'cancelar' significa "
            f"PAGAR o SALDAR el monto, NO anular ni revocar el pedido.]"
        )
    return mensaje


# ─────────────────────────────────────────────
#  Llamada al modelo
# ─────────────────────────────────────────────

def llamar_modelo(historial: list[dict]) -> str:
    try:
        respuesta = llm.chat.completions.create(
            model=LM_STUDIO_MODEL,
            messages=historial,
            temperature=TEMPERATURE,
        )
        return respuesta.choices[0].message.content

    except Exception as e:
        msg = str(e)
        if "n_ctx" in msg or "context length" in msg.lower() or "400" in msg:
            return (
                "⚠️  Error: el contexto del modelo es demasiado pequeño para los documentos cargados.\n"
                "Solución: en LM Studio → ⚙️ del modelo → aumenta 'Context Length' a 16384 o más, "
                "luego recarga el modelo."
            )
        raise  # otros errores sí los propagamos


def recortar_historial(historial: list[dict], max_turnos: int) -> list[dict]:
    """Conserva el system prompt + los últimos N turnos."""
    system = [historial[0]]
    turnos = historial[1:]
    if len(turnos) > max_turnos * 2:
        turnos = turnos[-(max_turnos * 2):]
    return system + turnos


# ─────────────────────────────────────────────
#  Bucle principal
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  🤖 BOT ATENCIÓN AL CLIENTE — IA-ATC")
    print("  Powered by LM Studio + Llama 3.1 + Firebase")
    print("=" * 60)
    print("  Escribe 'salir' para terminar.\n")

    datos_pedido  = None   # Se poblará cuando el cliente dé su ID
    pedido_buscado = False  # Para no repetir búsquedas fallidas con el mismo dato

    # Historial inicia sin datos de pedido (el bot pedirá el identificador)
    historial = [{"role": "system", "content": get_system_prompt(None)}]

    # Saludo inicial del bot
    print(f"{'─'*60}")
    print(f"🤖 María: {MENSAJE_BIENVENIDA}")
    print(f"{'─'*60}\n")
    historial.append({"role": "assistant", "content": MENSAJE_BIENVENIDA})

    # ── Bucle conversacional ─────────────────────────────────
    while True:
        try:
            mensaje_usuario = input("👤 Cliente: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nSesión interrumpida. ¡Hasta pronto!")
            break

        if not mensaje_usuario:
            continue
        if mensaje_usuario.lower() == "salir":
            print("\n🤖 María: ¡Hasta luego! Que tengas un excelente día. 😊")
            break

        # ── Extracción automática de identificador ───────────
        # Solo buscamos si aún no tenemos pedido
        if datos_pedido is None:
            resultado = intentar_obtener_pedido(mensaje_usuario)
            if resultado:
                datos_pedido = resultado
                nombre = f"{datos_pedido.get('clienteNombre','')} {datos_pedido.get('clienteApellidos','')}".strip()
                print(f"  [✅ Pedido encontrado: {nombre} | Estado: {datos_pedido.get('estadoGeneral')}]")
                historial[0] = {"role": "system", "content": get_system_prompt(datos_pedido)}

        # ── Si el cliente cuestiona el estado, re-consultar Firebase ──
        # Detecta frases como "me dijeron otra", "no es ese", "estaba en", etc.
        elif datos_pedido is not None:
            _REGEX_CUESTION_ESTADO = re.compile(
                r'\b(dijeron|dijiste|antes estaba|era otro|no es ese|diferente|cambi|otra etapa|otro estado)\b',
                re.IGNORECASE
            )
            if _REGEX_CUESTION_ESTADO.search(mensaje_usuario):
                id_pedido = datos_pedido.get('id', '')
                from firebase_client import buscar_pedido_por_id
                datos_frescos = buscar_pedido_por_id(id_pedido)
                if datos_frescos:
                    datos_pedido = datos_frescos
                    nuevo_estado = datos_pedido.get('estadoGeneral', 'N/A')
                    print(f"  [🔄 Re-consultado Firebase → Estado actual: {nuevo_estado}]")
                    historial[0] = {"role": "system", "content": get_system_prompt(datos_pedido)}

        # ── Preprocesar mensaje ───────────────────────────────
        # 1) Normalizar español informal (q→que, x→por, xq→porque, etc.)
        # 2) Aclarar 'cancelar' = pagar cuando el contexto lo indica
        mensaje_para_modelo = preprocesar_mensaje(normalizar_texto(mensaje_usuario))

        # ── Agregar mensaje del cliente al historial ─────────
        historial.append({"role": "user", "content": mensaje_para_modelo})
        historial = recortar_historial(historial, MAX_HISTORIAL_TURNOS)

        # ── Llamar al modelo ─────────────────────────────────
        print("🤔 Pensando...", end="", flush=True)
        respuesta_bot = llamar_modelo(historial)
        print("\r" + " " * 20 + "\r", end="")

        # ── Agregar respuesta al historial (memoria) ─────────
        historial.append({"role": "assistant", "content": respuesta_bot})

        print(f"🤖 María: {respuesta_bot}\n")
        print("─" * 60)


if __name__ == "__main__":
    main()

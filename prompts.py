# ============================================================
#  prompts.py — Personalidad, guía y contexto del bot de ATC
# ============================================================
from document_loader import cargar_multiples

from bot_manager import get_bot_prompt

def get_system_prompt(datos_pedido: dict | list[dict] | None = None, bot_id: str = "bot_wala") -> str:
    """
    Construye el system prompt en 2 bloques (Base de Agente + Datos dinámicos de Firebase).
    """
    
    # ── Bloque 1: guía completa (desde la base de bots) ─
    prompt = get_bot_prompt(bot_id)
    if not prompt:
        # Fallback de seguridad
        prompt = "Eres un asistente virtual de atención al cliente."

    # ── Bloque 2: datos del pedido (Firebase) ───────────────
    if datos_pedido:
        if isinstance(datos_pedido, dict):
            datos_pedido = [datos_pedido]
            
        prompt += "\n\n--- DATOS DE LOS PEDIDOS DEL CLIENTE (información real del sistema) ---\n"
        for i, pedido in enumerate(datos_pedido):
            nombre    = f"{pedido.get('clienteNombre', '')} {pedido.get('clienteApellidos', '')}".strip()
            estado    = pedido.get("estadoGeneral", "No disponible")
            id_pedido = pedido.get("id", "N/A")
            
            prompt += f"Pedido {i+1}:\n"
            prompt += f"- Nombre del cliente : {nombre}\n"
            prompt += f"- N° de pedido       : {id_pedido}\n"
            prompt += f"- Estado actual      : {estado}\n\n"
        prompt += "--- FIN DE DATOS ---\n"
        prompt += "IMPORTANTE: Si el cliente consulta sobre su pedido y el sistema te muestra información de MÁS DE UN PEDIDO, DEBES basar tu atención y responder asumiendo el pedido MÁS RECIENTE (Pedido 1). Sin embargo, si el cliente te aclara que no se refiere a ese pedido o menciona estar buscando otros, infórmale qué otros pedidos activos tiene en sistema (menciónalos) y pregúntale sobre cuál de ellos desea saber.\n"
    else:
        prompt += "\n\n--- DATOS DEL PEDIDO ---\nAún no tienes datos de ningún pedido específico.\nSolo pide el identificador si el cliente pregunta por SU pedido en particular.\n--- FIN DE DATOS ---\n"

    # ── Reglas globales anti-repetición ──────────────────────
    prompt += """
--- REGLAS CRÍTICAS DE COMPORTAMIENTO EN CONVERSACIÓN ---
1. ANTI-REPETICIÓN: Si en esta misma conversación ya informaste el estado del pedido del cliente, NO lo repitas en cada turno. Responde de forma natural y empática al mensaje puntual que el cliente acaba de escribir, como lo haría un humano en un chat real.
2. DESPEDIDA: Cuando el cliente se despide (dice "gracias", "ok", "hasta luego", "👍", etc. después de que tú ya le diste la información), responde con UNA despedida corta y el sticker [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/bendiciones.webp]. No añadas más información del pedido ni hagas más preguntas.
3. POST-DESPEDIDA: Si ya enviaste una despedida y el cliente responde solo para confirmar (con "ok", "gracias", "👍", "ya", "listo", etc.), NO respondas nada más. La conversación está finalizada.
--- FIN REGLAS ---
"""

    return prompt



MENSAJE_BIENVENIDA = (
    "¡Hola! 👋 Soy María, tu asistente de atención.\n"
    "¿En qué te puedo ayudar hoy? Puedo consultarte el estado de tu pedido. 😊"
)


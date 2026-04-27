import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the old block boundary
START_MARKER = '    # \u2500\u2500 Anti context-poisoning: corregir SOLO si el bot dijo un estado err\u00f3neo antes \u2500\u2500'
END_MARKER   = '    if historial_para_gemini and historial_para_gemini[-1]["role"] == "user":'

idx_start = content.find(START_MARKER)
idx_end   = content.find(END_MARKER, idx_start)

if idx_start == -1 or idx_end == -1:
    print("ERROR: markers not found")
    print("start:", idx_start, "end:", idx_end)
    # Try to show surrounding context
    sample = content[1449*1:1492*1]
    print("sample chars:", repr(content[idx_start-10:idx_start+60]))
else:
    new_block = '''    # -- Ancla de estado: previene alucinaciones ---
    # Inyecta el estado real antes de cada llamada a Gemini.
    # Modo 1 (estado ya comunicado): recordatorio silencioso - no repetir.
    # Modo 2 (estado nunca comunicado): correccion critica.
    if pedidos_actuales:
        _lista = pedidos_actuales if isinstance(pedidos_actuales, list) else [pedidos_actuales]
        _estado_actual = _lista[0].get("estadoGeneral", "")
        _id_pedido = _lista[0].get("id", "")
        if _estado_actual:
            _KWORDS = {
                "Preparacion":   ["preparaci"],
                "Preparaci\u00f3n":   ["preparaci"],
                "En Impresion":  ["impresi"],
                "Estampado":     ["estampado"],
                "Empaquetado":   ["empaquetado"],
                "En Reparto":    ["reparto", "camino", "agencia", "repartidor"],
                "Entregado":     ["entregado", "recibi"],
                "Finalizado":    ["finalizado", "cerrado", "disfrutando", "disfrut"],
            }
            _kws = _KWORDS.get(_estado_actual, [_estado_actual.lower()[:6]])
            _ya_comunicado = any(
                any(k in m.get("content", "").lower() for k in _kws)
                for m in historial_para_gemini if m.get("role") == "assistant"
            )
            if _ya_comunicado:
                _ancla = (
                    f"[SISTEMA - Recordatorio: el pedido #{_id_pedido} sigue en '{_estado_actual}'. "
                    f"NO repitas el estado. Responde de forma natural al mensaje actual del cliente.]"
                )
            else:
                _ancla = (
                    f"[CORRECCION CRITICA: El estado REAL del pedido #{_id_pedido} es '{_estado_actual}'. "
                    f"Usa UNICAMENTE este estado en tu respuesta, no inventes otro.]"
                )
            historial_para_gemini.insert(-1, {"role": "user", "content": _ancla})

    '''
    content = content[:idx_start] + new_block + content[idx_end:]
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK: block replaced successfully")
    print("new block starts at char:", idx_start)

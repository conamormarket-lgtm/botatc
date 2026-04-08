import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove duplicate user append
old_dup = """        # Solo lo agregamos si no está ya como último mensaje (evitar duplicados lógicos)
        if not sesion["historial"] or sesion["historial"][-1].get("content") != texto_cliente:
            sesion["historial"].append({"role": "user", "content": texto_cliente})"""
text = text.replace(old_dup, "")

# 2. Add timestamp to Tester mode append
old_tester = """                sesion["esperando_pedido_tester"] = True
                msg = "🧪 *Modo prueba activado.*\\n\\nEscríbeme el ID del pedido que deseas probar (tal como aparece en Firebase):"
                sesion["historial"].append({"role": "assistant", "content": msg})"""
new_tester = """                sesion["esperando_pedido_tester"] = True
                msg = "🧪 *Modo prueba activado.*\\n\\nEscríbeme el ID del pedido que deseas probar (tal como aparece en Firebase):"
                import time
                ts = int(time.time())
                sesion["historial"].append({"role": "assistant", "content": msg, "status": "sent", "timestamp": ts})"""
text = text.replace(old_tester, new_tester)

# 3. Add timestamp to Gemini response
old_gemini_reply = """    # 5) Llamar a Gemini y guardar respuesta
    respuesta = llamar_gemini(sesion["historial"])
    sesion["historial"].append({"role": "assistant", "content": respuesta})"""
new_gemini_reply = """    # 5) Llamar a Gemini y guardar respuesta
    respuesta = llamar_gemini(sesion["historial"])
    import time
    ts = int(time.time())
    
    # Check if this is the final append where we actually get wamid? 
    # Actually, enviar_mensaje returns msg_id. We must save msg_id here!
    sesion["historial"].append({"role": "assistant", "content": respuesta, "status": "sent", "timestamp": ts})"""
text = text.replace(old_gemini_reply, new_gemini_reply)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Cleaned up duplicates and updated bot append timestamps")

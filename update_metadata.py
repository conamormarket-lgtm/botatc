import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update webhook logic to handle statuses and add timestamp
old_webhook = """        # Ignorar eventos que no sean mensajes (ej: estados de entrega)
        if "messages" not in changes:
            return {"status": "ok"}

        mensaje_data  = changes["messages"][0]
        mensaje_id    = mensaje_data.get("id", "")"""

new_webhook = """        # Manejar estados de entrega (palomitas)
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
        mensaje_ts    = mensaje_data.get("timestamp", "")"""
text = text.replace(old_webhook, new_webhook)

# 2. Update incoming user message RAM append timestamp
old_ram = """    if not sesion["historial"] or sesion["historial"][-1].get("msg_id") != msg_id:
        sesion["historial"].append({"role": "user", "content": texto_cliente, "msg_id": msg_id})"""

new_ram = """    if not sesion["historial"] or sesion["historial"][-1].get("msg_id") != msg_id:
        import time
        ts = int(time.time()) # fallback
        sesion["historial"].append({"role": "user", "content": texto_cliente, "msg_id": msg_id, "timestamp": ts})"""
text = text.replace(old_ram, new_ram)

# 3. Update manual outgoing UI backend response append timestamp
old_out = """    if exito:
        s["historial"].append({"role": "assistant", "content": texto, "msg_id": msg_wamid})
        s["ultima_actividad"] = datetime.utcnow()"""

new_out = """    if exito:
        import time
        ts = int(time.time())
        s["historial"].append({"role": "assistant", "content": texto, "msg_id": msg_wamid, "status": "sent", "timestamp": ts})
        s["ultima_actividad"] = datetime.utcnow()"""
text = text.replace(old_out, new_out)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated metadata in webhook and manual send")

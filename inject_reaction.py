import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""        elif tipo_mensaje == "location":
            lat = mensaje_data.get("location", {}).get("latitude", "")
            lon = mensaje_data.get("location", {}).get("longitude", "")
            addr = mensaje_data.get("location", {}).get("address", "")
            texto_cliente = f"[ubicacion:{lat},{lon},{addr}]" """

replacement = r"""        elif tipo_mensaje == "reaction":
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
                texto_cliente = f"[❌ Quitó reacción a «{texto_original}»]"
        elif tipo_mensaje == "location":
            lat = mensaje_data.get("location", {}).get("latitude", "")
            lon = mensaje_data.get("location", {}).get("longitude", "")
            addr = mensaje_data.get("location", {}).get("address", "")
            texto_cliente = f"[ubicacion:{lat},{lon},{addr}]" """

if target in text:
    text = text.replace(target, replacement)
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced perfectly")
else:
    print("Target not found exactly")

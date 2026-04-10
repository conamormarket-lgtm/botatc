import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r'elif tipo_mensaje == "location":\n\s+lat = mensaje_data\.get\("location", \{\}\)\.get\("latitude", ""\)\n\s+lon = mensaje_data\.get\("location", \{\}\)\.get\("longitude", ""\)\n\s+addr = mensaje_data\.get\("location", \{\}\)\.get\("address", ""\)\n\s+texto_cliente = f"\[ubicacion:\{lat\},\{lon\},\{addr\}\]"\n\s+elif tipo_mensaje == "location":'

replacement = r"""elif tipo_mensaje == "reaction":
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
        elif tipo_mensaje == "location":"""

if re.search(target, text):
    text = re.sub(target, replacement, text)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced with regex!")
else:
    # Just try replacing the first occurrence
    target2 = r'elif tipo_mensaje == "location":'
    if target2 in text:
        replacement2 = r"""elif tipo_mensaje == "reaction":
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
                texto_cliente = f"💬 Reacción: {emoji} a «{texto_original}»"
            else:
                texto_cliente = f"❌ Quitó reacción a «{texto_original}»"
        elif tipo_mensaje == "location":"""
        text = text.replace(target2, replacement2, 1)
        with open("server.py", "w", encoding="utf-8") as f:
            f.write(text)
        print("Replaced direct match 1")

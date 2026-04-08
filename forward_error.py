import re
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's intercept whatsapp_client.enviar_media to return the error
old_enviar = '''        response = httpx.post(META_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        print(f"❌ Error Meta API ({e.response.status_code}): {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error enviando media ({tipo_media}): {e}")
        return None'''

new_enviar = '''        response = httpx.post(META_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("messages", [{}])[0].get("id")
    except httpx.HTTPStatusError as e:
        err_msg = e.response.text
        print(f"❌ Error Meta API ({e.response.status_code}): {err_msg}")
        return f"ERROR_META: {err_msg}"
    except Exception as e:
        print(f"❌ Error enviando media ({tipo_media}): {e}")
        return None'''

with open("whatsapp_client.py", "r", encoding="utf-8") as f:
    wa_text = f.read()

if 'ERROR_META:' not in wa_text:
    wa_text = wa_text.replace(old_enviar, new_enviar)
    with open("whatsapp_client.py", "w", encoding="utf-8") as f:
        f.write(wa_text)

# And in server.py process_and_send
old_process = '''            if w_id_current:
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
        return {"ok": False, "error": "META_API_REJECTED"}'''

new_process = '''            if w_id_current:
                if str(w_id_current).startswith("ERROR_META:"):
                    return False, w_id_current
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
        return {"ok": False, "error": msg_wamid if msg_wamid else "META_API_REJECTED"}'''

if 'start' not in text.split('if str(w_id_current).')[0][-100:]:
    text = text.replace(old_process, new_process)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)

print("Injected detailed error forwarding")

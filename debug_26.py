import json
try:
    with open('local_chats_master.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    pendientes = 0
    for k, v in data.items():
        if isinstance(v, dict):
            if v.get('unread_count', 0) > 0 and v.get('bot_activo', False):
                pendientes += 1
                hist = v.get("historial", [])
                last_msg = hist[-1] if hist else "None"
                print(f"Chat: {k}, Último msj: {last_msg}")
        else:
            print(f"Skipping string value for key: {k}")
    print(f"Total pendientes con bot activo: {pendientes}")
except Exception as e:
    print('Error:', e)

import firebase_client

res = firebase_client.cargar_sesion_chat('51949601522')
if not res: res = firebase_client.cargar_sesion_chat('949601522')
if not res: res = firebase_client.cargar_sesion_chat('principal_51949601522')

with open('test_output2.txt', 'w', encoding='utf-8') as f:
    for idx, msg in enumerate(res.get('historial', [])[:10]):
        f.write(f"{idx} [{msg.get('role')}] {repr(msg.get('content'))}\n")

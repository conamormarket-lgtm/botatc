import firebase_client
import sys

res = firebase_client.cargar_sesion_chat('51949601522')
if not res:
    res = firebase_client.cargar_sesion_chat('949601522')
if not res:
    res = firebase_client.cargar_sesion_chat('principal_51949601522')

if not res:
    print('No session found')
    sys.exit(0)

with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write(f"Bot activo: {res.get('bot_activo')}\n")
    for idx, msg in enumerate(res.get('historial', [])[-15:]):
        f.write(f"{idx} [{msg.get('role')}] {repr(msg.get('content'))}\n")

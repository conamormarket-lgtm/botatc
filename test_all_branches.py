import sys
sys.stdout.reconfigure(encoding='utf-8')

import traceback

try:
    s = open('server.py', 'r', encoding='utf-8').read()
    print("Read server.py")
except Exception as e:
    print("Error reading server.py", e)
    sys.exit(1)

import importlib
try:
    import firebase_client
    firebase_client.cargar_grupos_bd = lambda: [{"id": "vg_1", "name": "Grupo Testing", "members": []}]
    import server
    server.sesiones = {"51999999999": {"ultima_actividad": server.datetime.utcnow(), "historial": [], "bot_activo": True}}

    class MockRequest:
        def __init__(self, wa_id=None):
            self.cookies = {"admin_session": "active"}
            import starlette.datastructures
            self.query_params = starlette.datastructures.QueryParams()
            self.url = starlette.datastructures.URL("http://localhost/inbox" + ("/" + wa_id if wa_id else ""))

    res = server.renderizar_inbox(MockRequest())
    print("Success empty Inbox view")
    
    res2 = server.renderizar_inbox(MockRequest("51999999999"), wa_id="51999999999")
    print("Success real chat")

    res3 = server.renderizar_inbox(MockRequest("vg_1"), wa_id="vg_1")
    print("Success virtual group")

except Exception as e:
    print("Exception!")
    traceback.print_exc()

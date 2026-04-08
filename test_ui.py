import traceback
from server import app, renderizar_inbox
from fastapi.testclient import TestClient

class R:
    def __init__(self):
        self.cookies = {"admin_token": "algo"}

import server
server.verificar_sesion = lambda req: True
server.sesiones = {
    '123': {
        'ultima_actividad': '123',
        'bot_activo': True,
        'historial': [
            {'role': 'user', 'content': 'Hola', 'timestamp': 1665612984},
            {'role': 'assistant', 'content': 'Response', 'timestamp': 1665612985, 'status': 'read'}
        ]
    }
}

try:
    print(renderizar_inbox(R(), wa_id='123')[:100])
except Exception as e:
    traceback.print_exc()

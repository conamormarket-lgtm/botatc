import server
import traceback
from fastapi import Request
import starlette.datastructures
from datetime import datetime

class MockRequest:
    def __init__(self, wa_id=None):
        self.cookies = {"admin_session": "active"}
        self.query_params = starlette.datastructures.QueryParams()
        self.url = starlette.datastructures.URL("http://localhost/inbox")

server.sesiones = {
    "51999999999": {
        "historial": [
            {"role": "user", "content": "hola", "timestamp": "2024-01-01T00:00:00"}
        ],
        "ultima_actividad": datetime.utcnow()
    }
}
server.global_groups = [
    {
        "id": "vg_1",
        "name": "Test",
        "members": ["51999999999"]
    }
]

r = MockRequest()
try:
    res = server.renderizar_inbox(request=r)
    print("SUCCESS normal var")
except Exception as e:
    print("FAIL normal var")
    traceback.print_exc()

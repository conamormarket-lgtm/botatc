import server
import traceback
from fastapi import Request
import starlette.datastructures

class MockRequest:
    def __init__(self, wa_id=None):
        self.cookies = {"admin_session": "active"}
        self.query_params = starlette.datastructures.QueryParams()
        self.url = starlette.datastructures.URL("http://localhost/inbox")

r = MockRequest()
try:
    res = server.renderizar_inbox(request=r)
    print("SUCCESS normal")
except Exception as e:
    print("FAIL normal")
    traceback.print_exc()

r = MockRequest("vg_123")
try:
    res = server.renderizar_inbox(request=r, wa_id="vg_123")
    print("SUCCESS vg")
except Exception as e:
    print("FAIL vg")
    traceback.print_exc()

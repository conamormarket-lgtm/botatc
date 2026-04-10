import server
import traceback
from fastapi import Request

class MockRequest:
    def __init__(self):
        self.cookies = {"admin_session": "active"}

r = MockRequest()
try:
    res = server.renderizar_inbox(request=r)
    print("SUCCESS")
except Exception as e:
    print("FAIL")
    traceback.print_exc()

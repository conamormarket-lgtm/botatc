import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = 'app = FastAPI(title="Bot ATC — IA-ATC")'
rep = '''app = FastAPI(title="Bot ATC — IA-ATC")

import traceback
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    err_str = f"Unhandled exception: {exc}\\n{traceback.format_exc()}"
    with open("crash_log.txt", "w", encoding="utf-8") as file:
        file.write("\\n--- CRASH ---\\n")
        file.write(f"URL: {request.url}\\n")
        file.write(err_str)
    print(err_str)
    return JSONResponse(status_code=500, content={"message": "Internal Server Error", "details": str(exc)})
'''

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected crash logger into app")
else:
    print("Target not found")

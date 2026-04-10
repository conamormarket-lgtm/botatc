import asyncio
import httpx
import os
import sys

# Import config
sys.path.append(os.getcwd())
try:
    from config import META_ACCESS_TOKEN
except ImportError:
    print("Could not import META_ACCESS_TOKEN from config")
    sys.exit(1)

WABA_ID = '1127639386161077'
url = f'https://graph.facebook.com/v19.0/{WABA_ID}/message_templates'
print(url)
res = httpx.get(url, headers={'Authorization': f'Bearer {META_ACCESS_TOKEN}'})
print("status", res.status_code)
if res.status_code != 200:
    print(res.text)
else:
    data = res.json()
    for t in data.get('data', []):
        print(f"Name: {t.get('name')} | Lang: {t.get('language')} | Status: {t.get('status')}")

import urllib.request
import json
import sys
import os

# Import config
sys.path.append(os.getcwd())
res = []
try:
    from config import META_ACCESS_TOKEN, META_PHONE_NUMBER_ID
except ImportError:
    print("Could not import META_ACCESS_TOKEN from config")
    sys.exit(1)

wabas = ["1672706204042046", "1504314467711880", "1127639386161077", "1902705713768234"]
for waba in wabas:
    try:
        req = urllib.request.Request(
            f'https://graph.facebook.com/v19.0/{waba}/message_templates',
            headers={'Authorization': 'Bearer ' + META_ACCESS_TOKEN}
        )
        data = json.loads(urllib.request.urlopen(req).read().decode())
        print(f"WABA {waba} templates:")
        for t in data.get('data', []):
            print(f"  - {t.get('name')} ({t.get('language')})")
    except Exception as e:
        print(f"WABA {waba} fetch failed: {e}")

import httpx, os, json
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("META_ACCESS_TOKEN")
phone_id = os.getenv("META_PHONE_NUMBER_ID")

r = httpx.get(
    f"https://graph.facebook.com/v19.0/{phone_id}",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10
)
print(f"Status: {r.status_code}")
data = r.json()
if "error" in data:
    print(f"ERROR: {data['error']['message']}")
else:
    print("Token VALIDO permanentemente ✅")
    print(f"Numero: {data.get('display_phone_number', 'N/A')}")
    print(f"Nombre: {data.get('verified_name', 'N/A')}")
    print(f"Estado: {data.get('code_verification_status', 'N/A')}")

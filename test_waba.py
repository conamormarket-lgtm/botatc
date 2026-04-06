import os
import httpx
from dotenv import load_dotenv

load_dotenv()
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")
META_API_VERSION = "v19.0"

def run():
    headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
    
    # Intento 1: Get WABA from Phone Number ID
    url1 = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}"
    print(f"Requesting {url1}...")
    res1 = httpx.get(url1, headers=headers)
    print("Res1:", res1.status_code, res1.text)
    
    # Si conseguimos el WABA ID, podemos listar templates
    # res1 -> {"id": "...", "display_phone_number": "...", "name": "..."} NO WABA ID A VECES.
    # We can try to request field WABA_ID: `?fields=whatsapp_business_api_data` or `?fields=name_status,certificate`
    url_waba = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}?fields=name_status,certificate,whatsapp_business_api_data"
    res_waba = httpx.get(url_waba, headers=headers)
    print("Res_Waba:", res_waba.status_code, res_waba.text)

if __name__ == '__main__':
    run()

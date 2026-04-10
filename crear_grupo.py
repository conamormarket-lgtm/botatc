import asyncio
import httpx
from config import META_PHONE_NUMBER_ID, META_ACCESS_TOKEN

async def create_group(subject, description):
    url = f"https://graph.facebook.com/v20.0/{META_PHONE_NUMBER_ID}/groups"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "subject": subject,
        "description": description
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        print("Status:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    asyncio.run(create_group("Diseños Ventas Hoy", "Grupo oficial para subir imágenes de los pedidos."))

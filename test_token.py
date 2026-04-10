import asyncio
import httpx
from config import META_PHONE_NUMBER_ID, META_ACCESS_TOKEN

async def test_token():
    url = f"https://graph.facebook.com/v20.0/{META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": "1234567890", # fake format just to trigger syntax error, not 401
        "type": "text",
        "text": {"body": "test"}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        print("Status:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    asyncio.run(test_token())

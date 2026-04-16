import httpx
import asyncio

async def run():
    try:
        c = httpx.AsyncClient()
        r = await c.get('http://127.0.0.1:3000/api/qr/link')
        print("SUCCESS:", r.json())
        await c.aclose()
    except Exception as e:
        print('ERROR:', e, type(e))

if __name__ == '__main__':
    asyncio.run(run())

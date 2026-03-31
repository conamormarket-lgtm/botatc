import os
from google import genai
client = genai.Client(api_key='AIzaSyB1J-EwneaR0gCGRCiAmo68hhRTAyh1Gdw')
try:
    resp = client.models.generate_content(model='gemini-2.0-flash', contents='Hola')
    print('OK:', resp.text)
except Exception as e:
    import traceback
    traceback.print_exc()

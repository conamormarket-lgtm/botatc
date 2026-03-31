import os
import traceback
from google import genai
client = genai.Client(api_key='AIzaSyB1J-EwneaR0gCGRCiAmo68hhRTAyh1Gdw')
try:
    print(client.models.generate_content(model='gemini-2.5-flash', contents='Hola').text)
except Exception:
    traceback.print_exc()

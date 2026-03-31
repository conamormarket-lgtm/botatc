import os
from openai import OpenAI
client = OpenAI(api_key='AIzaSyB1J-EwneaR0gCGRCiAmo68hhRTAyh1Gdw', base_url='https://generativelanguage.googleapis.com/v1beta/openai/')
try:
    resp = client.chat.completions.create(model='gemini-1.5-flash', messages=[{'role': 'user', 'content': 'hola'}])
    print('OK', resp)
except Exception as e:
    import traceback
    traceback.print_exc()

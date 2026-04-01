import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
client = OpenAI(api_key=os.getenv('GEMINI_API_KEY'), base_url='https://generativelanguage.googleapis.com/v1beta/openai/')
try:
    resp = client.chat.completions.create(model='gemini-2.0-flash', messages=[{'role': 'user', 'content': 'hola'}])
    print('OK', resp)
except Exception as e:
    import traceback
    traceback.print_exc()

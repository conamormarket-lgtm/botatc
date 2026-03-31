from dotenv import load_dotenv
load_dotenv()
import os, groq
client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
try:
  resp = client.chat.completions.create(model='llama3-8b-8192', messages=[{'role': 'user', 'content': 'hola'}], max_tokens=10)
  print('OK:', resp.choices[0].message.content)
except Exception as e:
  print('ERROR:', e)

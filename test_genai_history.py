import os
from google import genai
from google.genai import types

client = genai.Client(api_key='AIzaSyB1J-EwneaR0gCGRCiAmo68hhRTAyh1Gdw')

historial = [
    {"role": "system", "content": "Eres un asistente feliz"},
    {"role": "user", "content": "hola"},
    {"role": "assistant", "content": "Hola! ¿En qué puedo ayudarte?"},
    {"role": "user", "content": "¿cómo te llamas?"}
]

system_text = historial[0]["content"]
gemini_contents = []
for msg in historial[1:]:
    role = "model" if msg["role"] == "assistant" else "user"
    # El SDK nuevo de Google acepta diccionarios simples:
    gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})

config = types.GenerateContentConfig(
    system_instruction=system_text,
    temperature=0.05,
    max_output_tokens=300,
)

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=gemini_contents,
    config=config
)
print("RESPUESTA:", resp.text)

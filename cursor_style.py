import re

with open("server.py", "r", encoding="utf-8") as f:
    s = f.read()

s = s.replace('display: inline-block;" alt="Imagen', 'display: inline-block; cursor: zoom-in;" alt="Imagen')

with open("server.py", "w", encoding="utf-8") as f:
    f.write(s)
print("Updated cursor style!")

with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Contexto del cierre del sidebar al usar QR
print('=== CIERRE QR (242943) ===')
print(repr(c[242800:243150]))

print()
print('=== PLANTILLAS HEADER (234579) ===')
print(repr(c[234450:234850]))

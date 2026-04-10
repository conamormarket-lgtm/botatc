import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("firebase_client.py", "r", encoding="utf-8") as f:
    text = f.read()

# Remove the broken section (lines 374-375: empty for body + duplicated functions) 
# The good copy starts from line 330 (CRLF, original) and then there's a duplicate from line 376 onwards
# Strategy: keep only one copy of the guardar/eliminar/cargar_grupos and USER MANAGEMENT sections

import re

# Remove the duplicated block: the first (broken) for loop and everything down to the duplicate
# The broken section is between "for doc in docs:\n\n" and "def guardar_grupo_bd"
# We want to replace that broken for loop and duplicates with just the clean version

bad_section = """    for doc in docs:\n\ndef guardar_grupo_bd(grupo: dict):\n    db = inicializar_firebase()\n    if db: db.collection("virtual_groups").document(grupo["id"]).set(grupo)\n\ndef eliminar_grupo_bd(grupo_id: str):\n    db = inicializar_firebase()\n    if db: db.collection("virtual_groups").document(grupo_id).delete()\n\ndef cargar_grupos_bd() -> list:\n    db = inicializar_firebase()\n    if not db: return []\n    docs = db.collection("virtual_groups").stream()\n    return [d.to_dict() for d in docs]\n\n\n# ─────────────────────────────────────────────\n#  USER AUTENTICATION AND MANAGEMENT\n# ─────────────────────────────────────────────\n\ndef crear_usuario(username: str, password_hash: str) -> bool:\n    db = inicializar_firebase()\n    doc_ref = db.collection("usuarios_atc").document(username)\n    if doc_ref.get().exists:\n        return False\n    doc_ref.set({\n        "password": password_hash,\n        "estado": "pendiente",\n        "permisos": []\n    })\n    return True\n\ndef obtener_usuario(username: str) -> dict | None:\n    db = inicializar_firebase()\n    doc = db.collection("usuarios_atc").document(username).get()\n    if doc.exists:\n        data = doc.to_dict()\n        data["username"] = username\n        return data\n    return None\n\ndef obtener_todos_los_usuarios() -> list[dict]:\n    db = inicializar_firebase()\n    docs = db.collection("usuarios_atc").get()\n    res = []\n    for doc in docs:\n        d = doc.to_dict()\n        d["username"] = doc.id\n        res.append(d)\n    return res\n\n"""

good_tail = """    for doc in docs:\n        d = doc.to_dict()\n        d["username"] = doc.id\n        res.append(d)\n    return res\n\n"""

# Find and fix the broken obtener_todos_los_usuarios
broken = '    for doc in docs:\n\ndef guardar_grupo_bd'
if broken in text:
    text = text.replace(broken, '    for doc in docs:\n        d = doc.to_dict()\n        d["username"] = doc.id\n        res.append(d)\n    return res\n\n\ndef guardar_grupo_bd')
    print("Fixed broken for loop")

# Now remove the duplicate block (second copy of guardar_grupo_bd through actualizar_permisos_usuario)
# Count how many times guardar_grupo_bd appears
count = text.count('def guardar_grupo_bd')
print(f"guardar_grupo_bd count: {count}")

if count > 1:
    # Remove from second occurrence onwards
    first_idx = text.find('def guardar_grupo_bd')
    second_idx = text.find('def guardar_grupo_bd', first_idx + 10)
    text = text[:second_idx]
    print("Removed duplicate block")

with open("firebase_client.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Done")

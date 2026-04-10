import sys

with open("firebase_client.py", "a", encoding="utf-8") as f:
    f.write("""

# ─────────────────────────────────────────────
#  USER AUTENTICATION AND MANAGEMENT
# ─────────────────────────────────────────────

def crear_usuario(username: str, password_hash: str) -> bool:
    db = inicializar_firebase()
    doc_ref = db.collection("usuarios_atc").document(username)
    if doc_ref.get().exists:
        return False
    doc_ref.set({
        "password": password_hash,
        "estado": "pendiente",
        "permisos": []
    })
    return True

def obtener_usuario(username: str) -> dict | None:
    db = inicializar_firebase()
    doc = db.collection("usuarios_atc").document(username).get()
    if doc.exists:
        data = doc.to_dict()
        data["username"] = username
        return data
    return None

def obtener_todos_los_usuarios() -> list[dict]:
    db = inicializar_firebase()
    docs = db.collection("usuarios_atc").get()
    res = []
    for doc in docs:
        d = doc.to_dict()
        d["username"] = doc.id
        res.append(d)
    return res

def actualizar_permisos_usuario(username: str, estado: str, permisos: list[str]) -> bool:
    db = inicializar_firebase()
    doc_ref = db.collection("usuarios_atc").document(username)
    if doc_ref.get().exists:
        doc_ref.update({
            "estado": estado,
            "permisos": permisos
        })
        return True
    return False
""")
print("Firebase functions appended")

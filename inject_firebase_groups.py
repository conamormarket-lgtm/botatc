import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("firebase_client.py", "r", encoding="utf-8") as f:
    text = f.read()

append_text = """
def guardar_grupo_bd(grupo: dict):
    db = inicializar_firebase()
    if db: db.collection("virtual_groups").document(grupo["id"]).set(grupo)

def eliminar_grupo_bd(grupo_id: str):
    db = inicializar_firebase()
    if db: db.collection("virtual_groups").document(grupo_id).delete()

def cargar_grupos_bd() -> list:
    db = inicializar_firebase()
    if not db: return []
    docs = db.collection("virtual_groups").stream()
    return [d.to_dict() for d in docs]
"""

if "def cargar_grupos_bd" not in text:
    with open("firebase_client.py", "a", encoding="utf-8") as f:
        f.write(append_text)
    print("Appended group functions to firebase_client.py")
else:
    print("Group functions already exist in firebase_client.py")

import sys
sys.path.insert(0, '.')

from firebase_client import inicializar_firebase

db = inicializar_firebase()

# Buscar y borrar el usuario admin de prueba en usuarios_atc
doc_ref = db.collection("usuarios_atc").document("admin")
doc = doc_ref.get()

if doc.exists:
    doc_ref.delete()
    print("Usuario 'admin' eliminado de usuarios_atc")
else:
    print("No se encontró usuario 'admin' en usuarios_atc (puede ser solo la cuenta de rescate hardcoded)")

# También limpiar cualquier sesión activa de ese usuario en auth_sessions
sessions = db.collection("auth_sessions").stream()
borradas = 0
for s in sessions:
    data = s.to_dict()
    if data.get("username") == "admin" and "admin1234" in str(data.get("password", "")):
        s.reference.delete()
        borradas += 1
        
print(f"Sesiones de prueba eliminadas: {borradas}")

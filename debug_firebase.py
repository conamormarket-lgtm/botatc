# ============================================================
#  debug_firebase.py — Script de diagnóstico para ver exactamente
#  cómo está guardado el clienteContacto en tus pedidos de Firebase
# ============================================================
import sys
sys.path.insert(0, '.')   # asegurar que importa desde esta carpeta

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

print("=" * 60)
print("  DIAGNÓSTICO: primeros 5 pedidos en Firebase")
print("=" * 60)

docs = db.collection("pedidos").limit(5).get()

for doc in docs:
    data = doc.to_dict()
    print(f"\n  ID documento : {doc.id}")
    print(f"  id (pedido)  : {repr(data.get('id'))}")
    print(f"  clienteContacto : {repr(data.get('clienteContacto'))}")
    print(f"  clienteNombre   : {repr(data.get('clienteNombre'))}")

print("\n" + "=" * 60)
print("Ahora buscando el teléfono 945257117 exactamente...")
docs2 = (
    db.collection("pedidos")
      .where(filter=FieldFilter("clienteContacto", "==", "945257117"))
      .get()
)
resultados = list(docs2)
if resultados:
    print(f"✅ Encontrado con '945257117' exacto!")
else:
    print("❌ No encontrado con '945257117' exacto.")
    print("   → El campo existe pero con otro formato, o ese número no tiene pedido.")

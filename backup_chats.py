import os
import io
import json
import zipfile
from datetime import datetime, timezone, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# =========================================================
# CONFIGURACION ARCHIVOS
# =========================================================
SERVICE_ACCOUNT_FILE = 'serviceAccountKey.json'
MASTER_DB_FILE = 'local_chats_master.json'
ZIP_FINAL_FILE = 'ultimo_backup_chats.zip'
# =========================================================

# Helper: Convertir datetimes para JSON
def json_serial(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not serializable")

def main():
    print("[BACKUP] Iniciando recoleccion nocturna Incremental...")

    # 1. Configurar credenciales Firestore
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    # 2. Cargar Master DB local si existe
    master_db = {}
    last_sync = None
    if os.path.exists(MASTER_DB_FILE):
        try:
            with open(MASTER_DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                master_db = data.get("chats", {})
                last_sync_str = data.get("last_sync")
                if last_sync_str:
                    last_sync = datetime.fromisoformat(last_sync_str)
                    print(f"[BACKUP] Master local cargado. Ultima migracion fue el: {last_sync}")
        except Exception as e:
            print(f"[BACKUP] Error parseando master DB: {e}. Reconstruyendo todo...")

    # 3. Descargar chats desde Firestore
    chats_ref = db.collection('chats_atc')
    if last_sync:
        print("[BACKUP] Escaneando actualizaciones (Solo chats modificados recientemente)...")
        docs = chats_ref.where('ultima_actividad', '>', last_sync).stream()
    else:
        print("[BACKUP] Primer escaneo total. Descargando todo...")
        docs = chats_ref.stream()

    nuevos_modificados = 0
    ahora = datetime.utcnow().replace(tzinfo=timezone.utc)
    
    for doc in docs:
        chat_data = doc.to_dict()
        master_db[doc.id] = chat_data
        nuevos_modificados += 1

    print(f"[BACKUP] Se absorbieron/actualizaron {nuevos_modificados} chats en la base offline.")

    # Guardar nueva version master plana
    with open(MASTER_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "last_sync": ahora.isoformat(),
            "chats": master_db
        }, f, default=json_serial, indent=2, ensure_ascii=False)

    # 4. Comprimir a ZIP para descarga estatica de la pagina
    print(f"[BACKUP] Comprimiendo el snapshot a {ZIP_FINAL_FILE}...")
    with zipfile.ZipFile(ZIP_FINAL_FILE, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(MASTER_DB_FILE, 'chats_historial_completo.json')
    
    print("[BACKUP] Tarea nocturna completada. Archivo listo para descarga via Web.")

if __name__ == '__main__':
    main()

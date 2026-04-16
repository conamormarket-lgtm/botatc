import firebase_admin
from firebase_admin import firestore
from firebase_client import inicializar_firebase

def migrate_collection(db, collection_name):
    print(f"Migrando colección: {collection_name}...")
    try:
        docs = db.collection(collection_name).stream()
        
        batch = db.batch()
        count = 0
        total = 0
        
        for doc in docs:
            data = doc.to_dict()
            if 'lineId' not in data:
                doc_ref = db.collection(collection_name).document(doc.id)
                batch.update(doc_ref, {'lineId': 'principal'})
                count += 1
                total += 1
                
                if count == 400: # El límite de Firebase por batch es 500
                    batch.commit()
                    print(f"  Avanzando: {total} registros actualizados en {collection_name}...")
                    batch = db.batch()
                    count = 0
                    
        if count > 0:
            batch.commit()
            print(f"  Finalizado: {total} registros actualizados en {collection_name}.")
        else:
            print(f"  Finalizado: Ningún documento vacío requirió actualización en {collection_name}.")
    except Exception as e:
        print(f"  [ERROR] Fallo en la colección {collection_name}: {e}")

def main():
    try:
        db = inicializar_firebase()
        print("====== INICIANDO MIGRACIÓN ZERO-DOWNTIME ======")
        migrate_collection(db, 'chats_atc')
        migrate_collection(db, 'bot_quick_replies')
        migrate_collection(db, 'bot_templates')
        print("====== MIGRACIÓN COMPLETADA CON ÉXITO ======")
    except Exception as e:
        print(f"Error crítico durante la migración: {e}")

if __name__ == "__main__":
    main()

from firebase_client import inicializar_firebase

def migrate_lines():
    db = inicializar_firebase()
    print("Migrating templates...")
    templates = db.collection("bot_templates").stream()
    tc = 0
    for doc in templates:
        data = doc.to_dict()
        if not data.get("line_id"):
            db.collection("bot_templates").document(doc.id).set({"line_id": "principal"}, merge=True)
            tc += 1
            
    print("Migrating quick replies...")
    qrs = db.collection("bot_quick_replies").stream()
    qc = 0
    for doc in qrs:
        data = doc.to_dict()
        if not data.get("line_id"):
            db.collection("bot_quick_replies").document(doc.id).set({"line_id": "principal"}, merge=True)
            qc += 1
            
    print(f"Migration complete: {tc} templates, {qc} quick replies updated.")

if __name__ == "__main__":
    migrate_lines()

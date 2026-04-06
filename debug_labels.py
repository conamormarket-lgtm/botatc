import os
from firebase_client import inicializar_firebase

def check():
    db = inicializar_firebase()
    docs = db.collection("bot_labels").stream()
    count = 0
    for d in docs:
        print(d.to_dict())
        count += 1
    print(f"Total: {count}")

check()

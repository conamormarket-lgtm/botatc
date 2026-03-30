# ============================================================
#  firebase_client.py — Consultas a Firestore con Admin SDK
# ============================================================
import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from config import FIREBASE_CREDENTIALS_PATH, FIREBASE_JSON, COLECCION_PEDIDOS


def inicializar_firebase():
    """Inicializa Firebase Admin una sola vez."""
    if not firebase_admin._apps:
        if FIREBASE_JSON:
            import json
            try:
                cred_dict = json.loads(FIREBASE_JSON)
                cred = credentials.Certificate(cred_dict)
            except Exception as e:
                raise ValueError(f"❌ Error parseando FIREBASE_JSON: {e}")
        else:
            if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"\n❌ No se encontró '{FIREBASE_CREDENTIALS_PATH}' ni la variable FIREBASE_JSON.\n"
                    "Genera la clave en Firebase Console → Configuración → Cuentas de servicio.\n"
                )
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            
        firebase_admin.initialize_app(cred)
    return firestore.client()


def _buscar(db, campo: str, valor: str) -> dict | None:
    """Busca un pedido por campo=valor. Sintaxis moderna de Firestore."""
    docs = (
        db.collection(COLECCION_PEDIDOS)
          .where(filter=FieldFilter(campo, "==", valor))
          .limit(1)
          .get()
    )
    for doc in docs:
        return doc.to_dict()
    return None


def buscar_pedido_por_telefono(telefono: str) -> list[dict]:
    """
    Busca por número de teléfono en clienteContacto tolerando espacios
    extraños introducidos manualmente desde el panel de control.
    """
    db = inicializar_firebase()

    # 1. Limpiar lo que escribió el cliente → solo dígitos
    digitos = telefono.replace(" ", "").replace("-", "").replace("+", "")

    # Quitar código de país peruano si viene incluido (51XXXXXXXXX)
    if digitos.startswith("51") and len(digitos) == 11:
        digitos = digitos[2:]

    # 2. Generar ambos formatos de búsqueda
    con_espacios = f"{digitos[:3]} {digitos[3:6]} {digitos[6:]}"  # '945 257 117'

    # 3. Cubrir posibles espacios accidentales en ambos polos (Firebase es exacto)
    variantes_busqueda = [
        digitos,
        f" {digitos}",
        f"{digitos} ",
        f" {digitos} ",
        con_espacios,
        f" {con_espacios}",
        f"{con_espacios} ",
        f" {con_espacios} "
    ]

    docs = (
        db.collection(COLECCION_PEDIDOS)
          .where(filter=FieldFilter("clienteContacto", "in", variantes_busqueda))
          .limit(5)
          .get()
    )
    
    resultados = []
    for doc in docs:
        resultados.append(doc.to_dict())
        
    return resultados


def buscar_pedido_por_id(numero_pedido: str) -> dict | None:
    """
    Busca por N° de pedido (campo id).
    Firebase guarda IDs siempre con 6 dígitos y ceros a la izquierda
    (ej: '007053', '000001'). Se normaliza automáticamente.
    """
    db = inicializar_firebase()

    try:
        numero_normalizado = str(int(numero_pedido)).zfill(6)  # '7053' → '007053'
    except ValueError:
        numero_normalizado = numero_pedido

    variantes = list(dict.fromkeys([numero_normalizado, numero_pedido]))

    for variante in variantes:
        resultado = _buscar(db, "id", variante)
        if resultado:
            return resultado

    return None

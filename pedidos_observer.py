import threading
from firebase_client import inicializar_firebase
from config import COLECCION_PEDIDOS
from whatsapp_client import enviar_mensaje


ORDEN_ETAPAS = {
    "Diseño": 1,
    "Impresión": 2,
    "Preparación": 3,
    "Estampado": 4,
    "Empaquetado": 5,
    "Despacho": 6,
    "Terminado": 7,
    "Cancelado": -1
}

# Cache en memoria para detectar cambios de estado al vuelo.
# Solamente se guardan las variables mínimas para optimizar RAM.
cache_pedidos = {}

def notificar_whatsapp(pedido: dict, mensaje: str):
    contacto = pedido.get("clienteContacto", "").strip()
    if not contacto:
        return
    numero = contacto.replace("+", "").replace(" ", "").replace("-", "")
    # Añade código de país si no lo tiene
    if len(numero) == 9 and numero.startswith("9"):
        numero = "51" + numero
        
    print(f"  [PROACTIVIDAD PROVINCIA] Enviando notificación a {numero}...")
    enviar_mensaje(numero, mensaje)

def _enviar_plantilla_1(pedido: dict):
    nombre = pedido.get("clienteNombre", "").strip()
    pedido_id = pedido.get("id", "N/A")
    mensaje = (
        f"Felicidades {nombre} 🎉 Tu cuenta está pagada al 100% y tu pedido {pedido_id} "
        f"acaba de pasar a preparación. 📦\n\n"
        f"En cuanto tu pedido avance a Estampado te avisaremos.\n\n"
        f"Puedes revisar el estado de tu pedido las 24 horas del día desde la web:\n"
        f"https://www.conamor.pe/cuenta/pedidos"
    )
    notificar_whatsapp(pedido, mensaje)

def _enviar_plantilla_2(pedido: dict, nueva_etapa: str):
    nombre = pedido.get("clienteNombre", "").strip()
    pedido_id = pedido.get("id", "N/A")
    mensaje = (
        f"Hola {nombre} 👋 Tu pedido {pedido_id} se encuentra en {nueva_etapa}.\n\n"
        f"Agradecemos tu paciencia, estamos comprometidos en terminar tu pedido lo más rápido posible "
        f"pero sobre todo cuidando que quede perfecto como si fuera para nosotros. "
        f"Nuevamente, gracias por tu paciencia. ❤️\n\n"
        f"Puedes revisar el estado de tu pedido las 24 horas del día desde la web:\n"
        f"https://www.conamor.pe/cuenta/pedidos"
    )
    notificar_whatsapp(pedido, mensaje)

def procesar_cambio_pedido(doc_id: str, pedido: dict):
    # Validar si aplica: Solo PROVINCIA
    provincia = pedido.get("clienteProvincia", "Lima Metropolitana")
    if not provincia or provincia.strip().lower() in ["lima metropolitana", "lima"]:
        return
        
    estado_nuevo = pedido.get("estadoGeneral", "")
    try: deuda_nueva = float(pedido.get("deudaTotal", 0))
    except: deuda_nueva = 0
        
    estado_viejo = cache_pedidos.get(doc_id, {}).get("estadoGeneral", "")
    deuda_vieja = cache_pedidos.get(doc_id, {}).get("deudaTotal", -1)
    
    # Prevenir alertas al cargar por primera vez un documento modificado
    if not estado_viejo or deuda_vieja == -1:
        return

    # Escenario 1: Acaba de pagar su deuda al 100% Y se encuentra en Preparación
    # (Puede haber llegado a Preparación en este instante, o ya estar allí y recién pagar)
    if estado_nuevo == "Preparación" and deuda_nueva == 0 and deuda_vieja > 0:
        _enviar_plantilla_1(pedido)
        return

    # Escenario 2: Cambio hacia una etapa posterior en estadoGeneral
    if estado_nuevo != estado_viejo:
        peso_nuevo = ORDEN_ETAPAS.get(estado_nuevo, 0)
        peso_viejo = ORDEN_ETAPAS.get(estado_viejo, 0)
        
        # Si avanza y es mayor que Diseño
        if peso_nuevo > peso_viejo and peso_nuevo > 1:
            # Revalidar Caso 1 inverso: si avanzó a Preparación y su deuda YA ERA 0 (pagó por adelantado)
            if estado_nuevo == "Preparación" and deuda_nueva == 0:
                _enviar_plantilla_1(pedido)
                return
                
            # Todas las demás etapas (o Preparación si aún debe)
            _enviar_plantilla_2(pedido, estado_nuevo)

def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        doc = change.document
        doc_data = doc.to_dict()
        doc_id = doc.id
        
        try:
            deuda = float(doc_data.get("deudaTotal", 0))
        except:
            deuda = 0
            
        estado = doc_data.get("estadoGeneral", "")
        
        # Minimizar RAM limitando lo guardado en cache_pedidos
        cache_data = {"estadoGeneral": estado, "deudaTotal": deuda}
        
        if change.type.name == "ADDED":
            # Al iniciar, carga todos los pedidos actuales sin notificar
            cache_pedidos[doc_id] = cache_data
        elif change.type.name == "MODIFIED":
            procesar_cambio_pedido(doc_id, doc_data)
            cache_pedidos[doc_id] = cache_data
        elif change.type.name == "REMOVED":
            cache_pedidos.pop(doc_id, None)

_observador_activado = False

def iniciar_observador_pedidos():
    global _observador_activado
    if _observador_activado:
        return
        
    _observador_activado = True
    db = inicializar_firebase()
    print("👀 Conectando observador proactivo de pedidos para provincias...")
    
    # Solo escuchamos pedidos que no estén Terminados ni Cancelados para ahorrar RAM
    # Si su base de datos no tiene índices, Firestore permite != o in, pero es más
    # ligero simplemente traer los que están en procesos activos.
    etapas_activas = ["Diseño", "Impresión", "Preparación", "Estampado", "Empaquetado", "Despacho"]
    
    col_ref = db.collection(COLECCION_PEDIDOS).where("estadoGeneral", "in", etapas_activas)
    
    # Mantenemos el watcher en background gestionado por firebase-admin
    col_ref.on_snapshot(on_snapshot)
    print("🟢 Observador Firestore activado exitosamente.")

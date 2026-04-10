import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = """    global global_labels
    if not global_labels:
        try:
            from firebase_client import cargar_etiquetas_bd
            global_labels = cargar_etiquetas_bd()
        except: pass

    if not verificar_sesion(request):"""

rep = """    global global_labels
    if not global_labels:
        try:
            from firebase_client import cargar_etiquetas_bd
            global_labels = cargar_etiquetas_bd()
        except: pass

    global global_groups
    if not global_groups:
        try:
            from firebase_client import cargar_grupos_bd
            global_groups = cargar_grupos_bd()
        except: pass

    if not verificar_sesion(request):"""

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected global_groups loader")
else:
    print("Target not found global_groups loader")

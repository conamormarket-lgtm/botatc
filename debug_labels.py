from firebase_client import cargar_todas_las_sesiones
sesiones = cargar_todas_las_sesiones()
print("Sesiones encontradas:", len(sesiones))
for wa_id, s in sesiones.items():
    if "etiquetas" in s and s["etiquetas"]:
        print(f"Chat {wa_id} tiene etiquetas: {s['etiquetas']}")
    elif "etiquetas" in s:
        print(f"Chat {wa_id} tiene array de etiquetas pero está vacío.")
    else:
        print(f"Chat {wa_id} NO tiene la propiedad 'etiquetas'.")

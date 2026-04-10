import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()


# 1. Global initialization
init_target = """global global_labels
global_labels = []"""
init_rep = """global global_labels
global_labels = []
global global_groups
global_groups = []"""
if init_target in text: text = text.replace(init_target, init_rep)

startup_target = """        from firebase_client import cargar_etiquetas_bd
        global global_labels
        global_labels = cargar_etiquetas_bd()
        print(f"✅ Se restauraron {len(global_labels)} etiquetas globales.")
    except Exception as e:"""
startup_rep = """        from firebase_client import cargar_etiquetas_bd, cargar_grupos_bd
        global global_labels, global_groups
        global_labels = cargar_etiquetas_bd()
        print(f"✅ Se restauraron {len(global_labels)} etiquetas globales.")
        global_groups = cargar_grupos_bd()
        print(f"✅ Se restauraron {len(global_groups)} grupos virtuales.")
    except Exception as e:"""
if startup_target in text: text = text.replace(startup_target, startup_rep)

# 2. Add API endpoints
api_target = """@app.post("/api/admin/labels/delete")"""
api_rep = """class GroupPayload(BaseModel):
    id: str
    name: str
    members: list[str]

@app.post("/api/admin/groups/save")
async def api_save_group(payload: GroupPayload, request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    global global_groups
    found = False
    for i, g in enumerate(global_groups):
        if g.get("id") == payload.id:
            global_groups[i] = payload.dict()
            found = True
            break
    if not found: global_groups.append(payload.dict())
    try:
        from firebase_client import guardar_grupo_bd
        guardar_grupo_bd(payload.dict())
    except: pass
    return {"ok": True}

@app.post("/api/admin/groups/delete")
async def api_delete_group(payload: GroupPayload, request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    global global_groups
    global_groups = [g for g in global_groups if g.get("id") != payload.id]
    try:
        from firebase_client import eliminar_grupo_bd
        eliminar_grupo_bd(payload.id)
    except: pass
    return {"ok": True}

@app.get("/api/admin/groups/list")
async def api_list_groups(request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403)
    global global_groups
    if not global_groups:
        try: 
            from firebase_client import cargar_grupos_bd
            global_groups = cargar_grupos_bd()
        except: pass
    return {"groups": global_groups}

@app.post("/api/admin/labels/delete")"""

if api_target in text: text = text.replace(api_target, api_rep)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Injected groups api into server.py")

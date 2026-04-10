import sys

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

import re

# Add user endpoints
rep = """
@app.get("/usuarios", response_class=HTMLResponse)
async def panel_usuarios(request: Request):
    if not es_admin(request):
        return RedirectResponse(url="/inbox", status_code=303)
        
    return obtener_usuarios_html()

@app.get("/api/usuarios/list")
async def api_usuarios_list(request: Request):
    if not es_admin(request):
        return {"error": "Unauthorized"}
    from firebase_client import obtener_todos_los_usuarios
    return obtener_todos_los_usuarios()

@app.post("/api/usuarios/update")
async def api_usuarios_update(request: Request, data: dict):
    if not es_admin(request):
        return {"error": "Unauthorized"}
    from firebase_client import actualizar_permisos_usuario
    username = data.get("username")
    estado = data.get("estado")
    permisos = data.get("permisos", [])
    if actualizar_permisos_usuario(username, estado, permisos):
        return {"ok": True}
    return {"ok": False}

def obtener_usuarios_html():
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Panel de Usuarios — IA-ATC</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@600;700&display=swap" rel="stylesheet">
        <style>
          :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #3b82f6; --danger: #ef4444; --success: #10b981; }
          body { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; padding: 20px; }
          .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 20px; margin-bottom: 20px; }
          h1 { font-family: 'Outfit'; margin: 0; }
          .btn { background: var(--primary); color: white; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; text-decoration: none; font-size: 14px; }
          table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 10px; overflow: hidden; }
          th, td { padding: 15px; text-align: left; border-bottom: 1px solid #334155; }
          th { background: #0f172a; font-weight: 600; text-transform: uppercase; font-size: 12px; color: #94a3b8; }
          .badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
          .badge.pendiente { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
          .badge.aprobado { background: rgba(16, 185, 129, 0.2); color: var(--success); }
          select { background: #334155; color: white; border: 1px solid #475569; padding: 5px 10px; border-radius: 5px; }
          .action-btn { background: #475569; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Gestión de Usuarios</h1>
            <div>
                <a href="/inbox" class="btn" style="background:#475569">← Volver al Inbox</a>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Usuario</th>
                    <th>Estado</th>
                    <th>Permisos</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id="users-body">
                <tr><td colspan="4" style="text-align:center">Cargando...</td></tr>
            </tbody>
        </table>

        <script>
            async function loadUsers() {
                const res = await fetch('/api/usuarios/list');
                const users = await res.json();
                const tbody = document.getElementById('users-body');
                tbody.innerHTML = '';
                
                users.forEach(u => {
                    const isAdmin = u.permisos.includes('admin');
                    tbody.innerHTML += `<tr>
                            <td>${u.username}</td>
                            <td><span class="badge ${u.estado}">${u.estado}</span></td>
                            <td>${isAdmin ? 'Admin' : 'Estándar'}</td>
                            <td>
                                <select id="estado-${u.username}">
                                    <option value="pendiente" ${u.estado === 'pendiente' ? 'selected' : ''}>Pendiente</option>
                                    <option value="aprobado" ${u.estado === 'aprobado' ? 'selected' : ''}>Aprobado</option>
                                </select>
                                <select id="permiso-${u.username}">
                                    <option value="">Estándar</option>
                                    <option value="admin" ${isAdmin ? 'selected' : ''}>Admin</option>
                                </select>
                                <button class="action-btn" onclick="saveUser('${u.username}')">Guardar</button>
                            </td>
                        </tr>`;
                });
            }
            
            async function saveUser(username) {
                const estado = document.getElementById(`estado-${username}`).value;
                const perm = document.getElementById(`permiso-${username}`).value;
                const permisos = perm ? [perm] : [];
                
                const res = await fetch('/api/usuarios/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, estado, permisos})
                });
                
                if (res.ok) {
                    alert("Usuario actualizado");
                    loadUsers();
                } else {
                    alert("Error al actualizar");
                }
            }
            
            loadUsers();
        </script>
    </body>
    </html>
    '''

@app.get("/")
"""

text = re.sub(r'@app\.get\("/"\)', lambda m: rep, text)

# Now iterate the endpoints and replace 'if not verificar_sesion(' with 'if not es_admin(' for admin routes.
# But inbox.html /inbox can use verificar_sesion.
admin_routes = [
    "/settings", "/admin", "/api/settings", "/api/admin", "/debug"
]

lines = text.split('\\n')
inside_admin_route = False

for i, line in enumerate(lines):
    if line.startswith("@app.get(") or line.startswith("@app.post(") or line.startswith("@app.delete("):
        inside_admin_route = any(r in line for r in admin_routes)
    
    if inside_admin_route and "if not verificar_sesion(request):" in line:
        lines[i] = line.replace("verificar_sesion", "es_admin")

text = '\\n'.join(lines)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Finished configuring user auth and endpoints")

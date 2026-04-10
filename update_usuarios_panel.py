import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# ─── 1. Tabla: agregar columna "Nombre Visible" ──────────────────────────
old_thead = """                    <th>Usuario</th>
                    <th>Estado</th>
                    <th>Permisos</th>
                    <th>Acciones</th>"""
new_thead = """                    <th>Usuario</th>
                    <th>Nombre Visible</th>
                    <th>Estado</th>
                    <th>Permisos</th>
                    <th>Acciones</th>"""
text = text.replace(old_thead, new_thead)

# ─── 2. Fila: mostrar nombre y campo editable ─────────────────────────
old_row = """                    tbody.innerHTML += `<tr>
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
                        </tr>`;"""

new_row = """                    tbody.innerHTML += `<tr>
                            <td>${u.username}</td>
                            <td><input type="text" id="nombre-${u.username}" value="${u.nombre || ''}" placeholder="Nombre visible..." style="background:#0f172a; color:white; border:1px solid #475569; padding:5px 8px; border-radius:5px; width:140px; font-size:13px;"></td>
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
                        </tr>`;"""
text = text.replace(old_row, new_row)

# ─── 3. saveUser: envíar el nombre ───────────────────────────────────
old_save = """            async function saveUser(username) {
                const estado = document.getElementById(`estado-${username}`).value;
                const perm = document.getElementById(`permiso-${username}`).value;
                const permisos = perm ? [perm] : [];
                
                const res = await fetch('/api/usuarios/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, estado, permisos})
                });"""
new_save = """            async function saveUser(username) {
                const estado = document.getElementById(`estado-${username}`).value;
                const perm = document.getElementById(`permiso-${username}`).value;
                const permisos = perm ? [perm] : [];
                const nombre = document.getElementById(`nombre-${username}`)?.value?.trim() || '';
                
                const res = await fetch('/api/usuarios/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, estado, permisos, nombre})
                });"""
text = text.replace(old_save, new_save)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Panel de usuarios actualizado con campo nombre")

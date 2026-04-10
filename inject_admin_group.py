import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("admin.html", "r", encoding="utf-8") as f:
    text = f.read()

target_html = """            <!-- GESTIÓN DE STICKERS -->"""
rep_html = """            <!-- GESTIÓN DE GRUPOS VIRTUALES -->
            <h3 class="section-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                Gestión de Grupos Virtuales
            </h3>
            <div class="table-card" style="padding: 2.5rem;">
                <p style="color:var(--text-muted); font-size:0.95rem; margin-bottom: 2rem;">Crea agrupaciones virtuales de números de WhatsApp para ver sus mensajes unificados en un solo "chat" en tu Bandeja de Entrada. Útil para monitorear equipos o proveedores en conjunto.</p>
                
                <div style="display:flex; gap:1rem; margin-bottom: 2rem; flex-wrap: wrap;">
                    <input type="text" id="vgName" placeholder="Nombre del Grupo (Ej. Proveedores)" style="flex:1; min-width:200px; padding:0.8rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--bg-main); color:white;">
                    <input type="text" id="vgNumbers" placeholder="Números separados por comas (Ej. 51999..., 51998...)" style="flex:2; min-width:300px; padding:0.8rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--bg-main); color:white;">
                    <button type="button" class="btn-action btn-primary" onclick="guardarGrupoVirtual()">+ Guardar Grupo</button>
                    <button type="button" class="btn-action btn-outline" id="btnCancelEditVg" style="display:none;" onclick="cancelarEdicionVg()">Cancelar</button>
                </div>

                <div id="vgListContainer">
                    <!-- Dynamic list here -->
                </div>
            </div>

            <!-- GESTIÓN DE STICKERS -->"""

if target_html in text:
    text = text.replace(target_html, rep_html)
    print("Injected HTML section")
else:
    print("HTML target not found")

target_js = """                e.target.value = ''; // Reset buffer
            }
        });
    </script>"""

rep_js = """                e.target.value = ''; // Reset buffer
            }
        });

        // Funciones para Grupos Virtuales
        async function cargarGruposVirtuales() {
            try {
                const res = await fetch('/api/admin/groups/list');
                if(!res.ok) return;
                const data = await res.json();
                const container = document.getElementById('vgListContainer');
                if(!data.groups || data.groups.length === 0) {
                    container.innerHTML = '<div style="text-align:center; color:var(--text-muted); font-style:italic; padding:2rem;">No hay grupos creados. Escribe arriba para configurar uno.</div>';
                    return;
                }
                
                let html = '<table class="admin-table"><thead><tr><th>Nombre</th><th>Miembros (Números)</th><th>Acciones</th></tr></thead><tbody>';
                data.groups.forEach(g => {
                    html += `<tr>
                        <td><strong>${g.name}</strong></td>
                        <td style="color:var(--text-muted); font-size:0.85rem; max-width: 400px; overflow:hidden; text-overflow:ellipsis;">${g.members.join(', ')}</td>
                        <td>
                            <button class="btn-action btn-outline" onclick="editarGrupoVirtual('${g.id}', '${g.name}', '${g.members.join(',')}')" style="margin-right:0.5rem;">Editar</button>
                            <button class="btn-action btn-primary" style="background-color:var(--danger-color)" onclick="eliminarGrupoVirtual('${g.id}')">Eliminar</button>
                        </td>
                    </tr>`;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            } catch(e) {}
        }

        let editGroupId = null;
        function editarGrupoVirtual(id, name, members) {
            editGroupId = id;
            document.getElementById('vgName').value = name;
            document.getElementById('vgNumbers').value = members;
            document.getElementById('btnCancelEditVg').style.display = 'inline-block';
        }

        function cancelarEdicionVg() {
            editGroupId = null;
            document.getElementById('vgName').value = '';
            document.getElementById('vgNumbers').value = '';
            document.getElementById('btnCancelEditVg').style.display = 'none';
        }

        async function guardarGrupoVirtual() {
            const name = document.getElementById('vgName').value.trim();
            const numsStr = document.getElementById('vgNumbers').value;
            const nums = numsStr.split(',').map(s => s.replace(/[^0-9]/g, '')).filter(s => s.length > 6);
            
            if(!name || nums.length === 0) {
                alert("Debes ingresar un nombre y al menos un número telefónico válido.");
                return;
            }
            
            const id = editGroupId || 'vg_' + Date.now();
            
            try {
                const res = await fetch('/api/admin/groups/save', {
                    method: 'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({id: id, name: name, members: nums})
                });
                if(res.ok) {
                    cancelarEdicionVg();
                    cargarGruposVirtuales();
                } else alert("Error guardando el grupo en el servidor.");
            } catch(e) { alert("Error de conexión al guardar el grupo."); }
        }

        async function eliminarGrupoVirtual(id) {
            if(!confirm("¿Seguro que deseas eliminar este grupo virtual?\\nLos chats individuales de estas personas no se borrarán, solo dejarán de agruparse visualmente.")) return;
            try {
                await fetch('/api/admin/groups/delete', {
                    method: 'POST', headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({id: id, name: '', members: []})
                });
                cargarGruposVirtuales();
            } catch(e) {}
        }

        document.addEventListener('DOMContentLoaded', () => {
            cargarGruposVirtuales();
        });
    </script>"""

if target_js in text:
    text = text.replace(target_js, rep_js)
    with open("admin.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected JS section")
else:
    print("JS target not found")

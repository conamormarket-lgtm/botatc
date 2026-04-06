import io
with open('inbox.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add css
html = html.replace('        .btn-responsive-back { display: flex; align-items: center; }\n        }', '        .btn-responsive-back { display: flex; align-items: center; }\n        }\n\n        .hide-scrollbar::-webkit-scrollbar { display: none; }\n        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }')

# 2. Add labels filters in header
header_target = '''            <div class="list-tabs">
                <a href="/inbox?tab=all" class="tab {tab_all_active}">Todos</a>
                <a href="/inbox?tab=human" class="tab {tab_human_active}">Humanos</a>
            </div>'''
            
header_replacement = '''            <div class="list-tabs">
                <a href="/inbox?tab=all" class="tab {tab_all_active}">Todos</a>
                <a href="/inbox?tab=human" class="tab {tab_human_active}">Humanos</a>
            </div>
            
            {labels_filter_html}'''
html = html.replace(header_target, header_replacement)

# 3. Add modal outside click logic
click_target = '''            const chatLabelMenu = document.getElementById("chatLabelMenu");
            if(chatLabelMenu && !e.target.closest('#chatLabelMenu') && !e.target.closest('button[title="Etiquetas del Chat"]')) {
                chatLabelMenu.style.display = "none";
            }
        });'''
click_replacement = '''            const chatLabelMenu = document.getElementById("chatLabelMenu");
            if(chatLabelMenu && !e.target.closest('#chatLabelMenu') && !e.target.closest('button[title="Etiquetas del Chat"]')) {
                chatLabelMenu.style.display = "none";
            }
            
            const filterMenu = document.getElementById('inboxFilterMenu');
            if(filterMenu && !e.target.closest('#inboxFilterMenu') && !e.target.closest('button') && !e.target.closest('svg')) {
                filterMenu.style.display = 'none';
            }
        });'''
html = html.replace(click_target, click_replacement)

# 4. Modify crearGlobalLabel
crear_target = '''        // ================= ETIQUETAS (LABELS) LOGIC =================
        async function crearGlobalLabel() {
            const name = prompt("Escribe el nombre de la nueva etiqueta (ej: Nuevo Cliente, Venta Cerrada):");
            if(!name) return;
            const color = prompt("Escribe un color en HEX (ej: #ef4444 para rojo, #3b82f6 para azul, #22c55e para verde, #f59e0b para naranja). Si lo dejas vacío, será gris:") || "#94a3b8";
            
            const id = 'lbl_' + Date.now();
            try {
                const res = await fetch("/api/admin/labels/save", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({id: id, name: name.trim(), color: color.trim()})
                });
                if(res.ok) cargarChatLabels();
            } catch(e) {
                alert("Error guardando etiqueta");
            }
        }'''
        
crear_replacement = '''        // ================= ETIQUETAS (LABELS) LOGIC =================
        function crearGlobalLabel() {
            // Abrir el modal en lugar de prompt()
            const modal = document.getElementById("createLabelModal");
            if (modal) {
                document.getElementById("newLabelName").value = "";
                // Reset a color por defecto
                const firstColor = document.getElementById("color-grid-container").querySelector('.color-option');
                if(firstColor) seleccionarColorEtiqueta("#3b82f6", firstColor);
                modal.style.display = "flex";
            }
        }
        
        async function guardarNuevaEtiquetaModal() {
            const nameInput = document.getElementById("newLabelName");
            if(!nameInput) return;
            const name = nameInput.value.trim();
            if(!name) return alert("Por favor, ingresa un nombre para la etiqueta.");
            
            const color = document.getElementById("newLabelColor").value || "#94a3b8";
            const id = 'lbl_' + Date.now();
            
            try {
                const res = await fetch("/api/admin/labels/save", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({id: id, name: name, color: color})
                });
                if(res.ok) {
                    document.getElementById("createLabelModal").style.display = "none";
                    cargarChatLabels();
                } else {
                    alert("Error guardando etiqueta (Respuesta del servidor).");
                }
            } catch(e) {
                alert("Error guardando etiqueta (Conectividad).");
            }
        }'''
html = html.replace(crear_target, crear_replacement)

# 5. Add Modal before </body>
modal_html = '''
    <!-- Modal de Creación de Etiqueta (Tipo WhatsApp Business) -->
    <div id="createLabelModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:9999; align-items:center; justify-content:center;">
        <div style="background:var(--bg-main); border:1px solid var(--accent-border); border-radius:12px; width:350px; flex-direction:column; box-shadow:0 10px 25px rgba(0,0,0,0.5); overflow:hidden;">
            <div style="padding:1rem; border-bottom:1px solid var(--accent-border); display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin:0; font-family:var(--font-heading); font-size:1.1rem;">Añadir etiqueta</h3>
                <button onclick="document.getElementById('createLabelModal').style.display='none'" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.5rem;">&times;</button>
            </div>
            
            <div style="padding:1.5rem;">
                <label style="display:block; font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem; font-weight:500;">Nombre de etiqueta</label>
                <input type="text" id="newLabelName" placeholder="Ej: Nuevo Cliente" style="width:100%; padding:0.6rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); font-size:0.9rem; outline:none; margin-bottom:1.5rem;">
                
                <label style="display:block; font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem; font-weight:500;">Color</label>
                <input type="hidden" id="newLabelColor" value="#3b82f6"> <!-- default: blue -->
                <div id="color-grid-container" style="display:grid; grid-template-columns:repeat(5, 1fr); gap:0.6rem; margin-bottom:1.5rem;">
                    <script>
                        const predefinedColors = ["#ef4444", "#f97316", "#f59e0b", "#eab308", "#84cc16", "#22c55e", "#10b981", "#14b8a6", "#06b6d4", "#0ea5e9", "#3b82f6", "#6366f1", "#8b5cf6", "#a855f7", "#d946ef", "#ec4899", "#f43f5e", "#64748b", "#78716c", "#52525b"];
                        let colorsHtml = '';
                        predefinedColors.forEach((color, idx) => {
                            const isSelected = idx === 10 ? 'box-shadow: 0 0 0 2px var(--bg-main), 0 0 0 4px ' + color + ';' : 'border:2px solid transparent;';
                            colorsHtml += `<button type="button" class="color-option" style="width:100%; aspect-ratio:1; border-radius:50%; background:${color}; cursor:pointer; ${isSelected} transition:transform 0.1s;" onclick="seleccionarColorEtiqueta('${color}', this)"></button>`;
                        });
                        document.write(colorsHtml);
                        
                        function seleccionarColorEtiqueta(color, element) {
                            document.getElementById("newLabelColor").value = color;
                            const options = document.querySelectorAll('.color-option');
                            options.forEach(opt => {
                                opt.style.boxShadow = 'none';
                                opt.style.border = '2px solid transparent';
                            });
                            element.style.boxShadow = `0 0 0 2px var(--bg-main), 0 0 0 4px ${color}`;
                        }
                    </script>
                </div>
                
                <div style="display:flex; justify-content:flex-end; gap:0.5rem;">
                    <button type="button" onclick="document.getElementById('createLabelModal').style.display='none'" style="padding:0.6rem 1rem; border-radius:6px; background:none; border:none; color:var(--text-main); font-weight:600; cursor:pointer;">Cancelar</button>
                    <button type="button" onclick="guardarNuevaEtiquetaModal()" style="padding:0.6rem 1rem; border-radius:6px; background:var(--primary-color); border:none; color:white; font-weight:600; cursor:pointer;">Guardar</button>
                </div>
            </div>
        </div>
    </div>
"""
html = html.replace('</body>', modal_html + '\n</body>')

with open('inbox.html', 'w', encoding='utf-8') as f:
    f.write(html)

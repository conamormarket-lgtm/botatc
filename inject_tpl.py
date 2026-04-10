import sys
import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

btn_html = """
            <div style="padding: 0 20px 10px 20px;">
                <button onclick="openTemplateModal()" class="dashboard-btn" style="width: 100%; background: var(--success-color); border:none; border-radius:10px; font-weight:600; cursor:pointer;">
                    💬 Nueva Conversación
                </button>
            </div>
"""

# Insert under {labels_filter_html}
text = text.replace('{labels_filter_html}', '{labels_filter_html}' + btn_html)

modal_html = """
    <!-- Modal: Start Template Conversation -->
    <div class="modal-overlay" id="template-modal">
        <div class="modal">
            <h2 style="margin-bottom: 10px; font-family:var(--font-heading);">Nueva Conversación (Plantilla)</h2>
            <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 20px;">
                Inicia un contacto saliente usando una plantilla aprobada por Meta.
            </p>
            <div style="margin-bottom: 15px;">
                <label style="display:block; margin-bottom:5px; font-weight:600;">Teléfono destino (con código de país)</label>
                <input type="text" id="tpl-phone" placeholder="Ej: 51987654321" style="width:100%; padding:10px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:white;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display:block; margin-bottom:5px; font-weight:600;">Nombre de la plantilla</label>
                <input type="text" id="tpl-name" placeholder="Ej: hello_world" style="width:100%; padding:10px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:white;">
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display:block; margin-bottom:5px; font-weight:600;">Variables ({{1}}, {{2}}... separadas por comas)</label>
                <input type="text" id="tpl-vars" placeholder="Pedro, 12345" style="width:100%; padding:10px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:white;">
                <small style="color:var(--text-muted); display:block; margin-top:5px;">Deja vacío si tu plantilla no tiene variables redaccionadas en el cuerpo.</small>
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                <button class="btn btn-secondary" onclick="closeTemplateModal()">Cancelar</button>
                <button class="btn btn-primary" onclick="sendTemplate()" id="tpl-send-btn">Enviar Mensaje</button>
            </div>
        </div>
    </div>
"""

js_html = """
        function openTemplateModal() {
            document.getElementById('template-modal').classList.add('active');
        }
        function closeTemplateModal() {
            document.getElementById('template-modal').classList.remove('active');
            document.getElementById('tpl-phone').value = '';
            document.getElementById('tpl-name').value = '';
            document.getElementById('tpl-vars').value = '';
        }
        async function sendTemplate() {
            const phone = document.getElementById('tpl-phone').value.trim();
            const name = document.getElementById('tpl-name').value.trim();
            const rawVars = document.getElementById('tpl-vars').value;
            
            if (!phone || !name) {
                alert("Teléfono y nombre de plantilla son obligatorios");
                return;
            }
            
            let vars = [];
            if (rawVars.trim()) {
                vars = rawVars.split(',').map(s => s.trim());
            }
            
            const btn = document.getElementById('tpl-send-btn');
            btn.innerText = "Enviando...";
            btn.disabled = true;
            
            try {
                const res = await fetch('/api/admin/enviar_plantilla', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        wa_id: phone,
                        template_name: name,
                        language_code: 'es',
                        body_params: vars
                    })
                });
                if (res.ok) {
                    alert("¡Plantilla enviada con éxito! El chat aparecerá en la bandeja actual si responde o recargas.");
                    closeTemplateModal();
                } else {
                    const err = await res.json();
                    alert("Error enviando: " + (err.detail || JSON.stringify(err)));
                }
            } catch (e) {
                alert("Error de red.");
            }
            
            btn.innerText = "Enviar Mensaje";
            btn.disabled = false;
        }
"""

if "template-modal" not in text:
    text = text.replace('</body>', modal_html + '\n</body>')
    text = text.replace('</script>\n</body>', js_html + '\n</script>\n</body>')

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Injected template UI into inbox.html")

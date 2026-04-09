import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Extract the existing renderQuickReplies function
start_str = "            function renderQuickReplies(data) {"
start_idx = text.find(start_str)
if start_idx == -1:
    print("Function start not found")
    exit()

end_str = "        function filtrarQuickReplies(val) {"
end_idx = text.find(end_str, start_idx)
if end_idx == -1:
    print("Function end not found")
    exit()

old_func_block = text[start_idx:end_idx]

# Build the new function
new_func_block = """            function renderQuickReplies(data) {
                const list = document.getElementById("quickRepliesList");
                if(!list) return;
                if(data.length === 0) {
                    list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:1rem; text-align:center;">Sin respuestas rápidas en el sistema.</div>`;
                    return;
                }
                list.innerHTML = "";
                
                // Agrupar por categoría
                const groups = {};
                data.forEach(qr => {
                    const cat = qr.category && qr.category.trim() !== "" ? qr.category : "General";
                    if(!groups[cat]) groups[cat] = [];
                    groups[cat].push(qr);
                });
                
                // Variables de control de estado abierto (mantener abiertos los grupos al buscar)
                const isSearching = document.getElementById('qrSearchFilter') && document.getElementById('qrSearchFilter').value.trim() !== "";
                
                Object.keys(groups).sort().forEach(cat => {
                    const groupContainer = document.createElement("div");
                    groupContainer.style.cssText = "display:flex; flex-direction:column; gap:0.4rem; margin-bottom:0.2rem;";
                    
                    const catHeader = document.createElement("div");
                    catHeader.style.cssText = "background:rgba(255,255,255,0.05); padding:0.6rem 0.8rem; border-radius:6px; cursor:pointer; display:flex; justify-content:space-between; align-items:center; font-weight:600; font-size:0.85rem; border:1px solid var(--accent-border); user-select:none; transition:background 0.2s;";
                    catHeader.onmouseover = function() {this.style.background='rgba(255,255,255,0.08)';};
                    catHeader.onmouseout = function() {this.style.background='rgba(255,255,255,0.05)';};
                    
                    const catTitle = document.createElement("span");
                    catTitle.innerText = cat + " (" + groups[cat].length + ")";
                    
                    const catIcon = document.createElement("span");
                    catIcon.innerHTML = "▼";
                    catIcon.style.cssText = "font-size:0.75rem; transition:transform 0.2s;";
                    if (!isSearching && cat !== "General" && cat !== "General (0)") {
                        catIcon.style.transform = "rotate(-90deg)"; // Closed by default unless it's General
                    }
                    
                    catHeader.appendChild(catTitle);
                    catHeader.appendChild(catIcon);
                    
                    const catContent = document.createElement("div");
                    catContent.style.cssText = "display:flex; flex-direction:column; gap:0.6rem; margin-top:0.2rem;";
                    
                    // Manage default state
                    if (!isSearching && cat !== "General") {
                        catContent.style.display = "none";
                    }
                    
                    catHeader.onclick = () => {
                        if (catContent.style.display === "none") {
                            catContent.style.display = "flex";
                            catIcon.style.transform = "rotate(0deg)";
                        } else {
                            catContent.style.display = "none";
                            catIcon.style.transform = "rotate(-90deg)";
                        }
                    };
                    
                    groupContainer.appendChild(catHeader);
                    groupContainer.appendChild(catContent);
                    list.appendChild(groupContainer);
                
                    groups[cat].forEach(qr => {
                        const container = document.createElement("div");
                        container.style.cssText = "display:flex; flex-direction:column; background:var(--accent-bg); padding:0.65rem 0.75rem; border-radius:8px; border:1px solid var(--accent-border); transition:border-color 0.15s; position:relative;";
                        container.onmouseover = function() {this.style.borderColor='var(--primary-color)';};
                        container.onmouseout = function() {this.style.borderColor='var(--accent-border)';};
                        const btn = document.createElement("button");
                        btn.type = "button";
                        btn.style.cssText = "background:none; border:none; text-align:left; cursor:pointer; color:var(--text-main); width:100%; display:flex; flex-direction:column; gap:0.25rem;";
                        const headerRow = document.createElement("div");
                        headerRow.style.cssText = "display:flex; justify-content:space-between; align-items:center; width:100%;";
                        const titleWrap = document.createElement("div");
                        titleWrap.style.cssText = "display:flex; align-items:center; gap:0.4rem; flex-wrap:wrap;";
                        const titleEl = document.createElement("strong");
                        titleEl.innerText = qr.title || qr.category || '(sin título)';
                        titleEl.style.fontSize = "0.88rem";
                        titleWrap.appendChild(titleEl);
                        const editBtn = document.createElement("button");
                        editBtn.innerHTML = "✎";
                        editBtn.title = "Editar";
                        editBtn.style.cssText = "background:none; border:none; color:var(--primary-color); cursor:pointer; padding:0 0.2rem; font-size:0.9rem; margin-right:1.4rem; flex-shrink:0;";
                        editBtn.onclick = (e) => { e.stopPropagation(); abrirModalCrearQR(qr.id); };
                        headerRow.appendChild(titleWrap);
                        headerRow.appendChild(editBtn);
                        btn.appendChild(headerRow);
                        const msgs = qr.mensajes || [];
                        const previewParts = msgs.slice(0,3).map(m => {
                            if(typeof m === 'string') return m;
                            if(m.type === 'text') return m.content || '';
                            if(m.type === 'image') return '🖼 Imagen';
                            if(m.type === 'video') return '🎬 Video';
                            if(m.type === 'audio') return '🎵 Audio';
                            return '[media]';
                        });
                        const prev = document.createElement("span");
                        prev.style.cssText = "font-size:0.78rem; color:var(--text-muted); line-height:1.3; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;";
                        prev.innerText = previewParts.join(' → ') + (msgs.length > 3 ? ' ...' : '') + (msgs.length > 1 ? ` (${msgs.length} msgs)` : '');
                        btn.appendChild(prev);
                        if(qr.etiquetas && qr.etiquetas.length > 0) {
                            const labelsRow = document.createElement("div");
                            labelsRow.style.cssText = "display:flex; flex-wrap:wrap; gap:0.3rem; margin-top:0.2rem;";
                            qr.etiquetas.forEach(lid => {
                                const lbl = (window._globalLabels||[]).find(l=>l.id===lid);
                                if(!lbl) return;
                                const badge = document.createElement("span");
                                badge.style.cssText = `background:${lbl.color}22; color:${lbl.color}; font-size:0.62rem; padding:0.1rem 0.35rem; border-radius:3px; border:1px solid ${lbl.color}44; font-weight:600;`;
                                badge.innerText = lbl.name;
                                labelsRow.appendChild(badge);
                            });
                            btn.appendChild(labelsRow);
                        }
                        btn.onclick = () => aplicarQuickReply(qr.id);
                        const delBtn = document.createElement("button");
                        delBtn.innerHTML = "×";
                        delBtn.title = "Eliminar";
                        delBtn.style.cssText = "position:absolute; top:0.4rem; right:0.4rem; background:rgba(0,0,0,0.3); border:none; color:#ef4444; border-radius:50%; width:18px; height:18px; display:flex; justify-content:center; align-items:center; cursor:pointer; opacity:0; transition:opacity 0.2s; font-size:0.75rem;";
                        container.onmouseenter = () => { delBtn.style.opacity = "1"; };
                        container.onmouseleave = () => { delBtn.style.opacity = "0"; };
                        delBtn.onclick = (e) => { e.stopPropagation(); eliminarQR(qr.id); };
                        container.appendChild(btn);
                        container.appendChild(delBtn);
                        catContent.appendChild(container);
                    });
                });
            }

"""

new_text = text[:start_idx] + new_func_block + text[end_idx:]

with open("server.py", "w", encoding="utf-8") as f:
    f.write(new_text)

print("Replaced!")

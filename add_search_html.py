import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update HTML containers
old_container = '''<div class="chats-container">
            {lista_chats_html}
        </div>'''
new_container = '''<div class="chats-container" id="regularChatsContainer">
            {lista_chats_html}
        </div>
        <div class="chats-container" id="msgSearchResults" style="display:none; padding:1rem; flex-direction:column; gap:5px; background:var(--bg-main);">
        </div>'''

if 'id="msgSearchResults"' not in text:
    text = text.replace(old_container, new_container)

# 2. Update JavaScript function
old_filter = '''window.aplicarFiltroChats = function () {
            const input = document.getElementById('chatSearchInput');
            if (!input) return;
            const val = input.value.toLowerCase().trim();
            const rows = document.querySelectorAll('.chat-row');
            let isPhoneNum = /^[0-9+ ]+$/.test(val) && val.replace(/\D/g, '').length >= 9;

            rows.forEach(row => {
                const name = row.querySelector('.chat-name').innerText.toLowerCase();
                const phone = row.getAttribute('href') || "";
                if (name.includes(val) || phone.includes(val)) {
                    row.style.display = 'block';
                } else {
                    row.style.display = 'none';
                }
            });

            const btn = document.getElementById('btnNewChat');
            if (btn) {
                if (isPhoneNum) {
                    btn.style.display = 'block';
                } else {
                    btn.style.display = 'none';
                }
            }
        };'''

new_filter = '''window.aplicarFiltroChats = function () {
            const input = document.getElementById('chatSearchInput');
            if (!input) return;
            const val = input.value.toLowerCase().trim();
            
            // Limit search scope to regular container so we don't accidentally hide our own search results
            const regularCont = document.getElementById('regularChatsContainer');
            const rows = regularCont ? regularCont.querySelectorAll('.chat-row') : document.querySelectorAll('.chat-row:not(#msgSearchResults .chat-row)');
            
            let isPhoneNum = /^[0-9+ ]+$/.test(val) && val.replace(/\\D/g, '').length >= 9;

            rows.forEach(row => {
                const nameNode = row.querySelector('.chat-name');
                const name = nameNode ? nameNode.innerText.toLowerCase() : "";
                const phone = row.getAttribute('href') || "";
                if (name.includes(val) || phone.includes(val)) {
                    row.style.display = 'block';
                } else {
                    row.style.display = 'none';
                }
            });

            const btn = document.getElementById('btnNewChat');
            if (btn) {
                btn.style.display = isPhoneNum ? 'block' : 'none';
            }

            const searchCont = document.getElementById('msgSearchResults');
            if(searchCont) {
                if(val.length >= 3 && !isPhoneNum) {
                    if(window.searchTimeout) clearTimeout(window.searchTimeout);
                    window.searchTimeout = setTimeout(async () => {
                        try {
                            const res = await fetch(`/api/admin/buscar_mensajes?q=${encodeURIComponent(val)}`);
                            const data = await res.json();
                            if(data.ok && data.resultados && data.resultados.length > 0) {
                                let localChatsFound = 0; rows.forEach(r => {if(r.style.display==='block') localChatsFound++;});
                                if (localChatsFound === 0 && regularCont) regularCont.style.display = 'none';
                                
                                let html = `<div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem; padding-left:0.5rem; text-transform:uppercase; letter-spacing:1px;">Mensajes (${data.resultados.length})</div>`;
                                data.resultados.forEach(r => {
                                    r.matches.forEach(m => {
                                        let icon = m.role === 'assistant' ? '🤖' : '👤';
                                        html += `
                                        <a href="/inbox/${r.wa_id}" class="chat-row search-msg-row" style="display:block; text-decoration:none; background:var(--accent-bg); border-radius:8px; margin-bottom:0.5rem; padding:0.8rem; border:1px solid transparent; transition:border 0.2s;">
                                            <div style="font-weight:600; color:var(--text-main); font-size:0.9rem; margin-bottom:0.3rem; display:flex; justify-content:space-between;">
                                                <span>${r.nombre}</span>
                                            </div>
                                            <div style="color:var(--text-muted); font-size:0.8rem; line-height:1.4; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;">
                                                <span style="opacity:0.6; margin-right:4px;">${icon}</span>${m.snippet.replace(new RegExp(val, "gi"), match => `<mark style="background:var(--primary-color); color:white; padding:0 2px; border-radius:2px;">${match}</mark>`)}
                                            </div>
                                        </a>`;
                                    });
                                });
                                searchCont.innerHTML = html;
                                searchCont.style.display = 'flex';
                            } else {
                                searchCont.style.display = 'none';
                                if(regularCont) regularCont.style.display = 'block';
                            }
                        } catch(e) { console.error('Global search error', e); }
                    }, 500); 
                } else {
                    if(window.searchTimeout) clearTimeout(window.searchTimeout);
                    searchCont.style.display = 'none';
                    if(regularCont) regularCont.style.display = 'block';
                }
            }
        };'''

if 'regularCont = document.getElementById(' not in text:
    text = text.replace(old_filter, new_filter)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)
    
print("Injected global message search into HTML")

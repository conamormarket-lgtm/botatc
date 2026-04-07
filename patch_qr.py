import re

code = open('server.py', 'r', encoding='utf-8').read()

# 1. Update the buttons list to include a new button for Tag Action
old_buttons = '''                                    <button onclick="addQrMessageField('text')" style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); color:var(--success-color); font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">+ Texto</button>
                                    <button onclick="addQrMessageField('image')" style="background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); color:var(--primary-color); font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🖼 Img</button>
                                    <button onclick="addQrMessageField('video')" style="background:rgba(139,92,246,0.15); border:1px solid rgba(139,92,246,0.3); color:#a78bfa; font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🎬 Vid</button>
                                    <button onclick="addQrMessageField('audio')" style="background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.3); color:#fbbf24; font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🎵 Audio</button>'''

new_buttons = '''                                    <button onclick="addQrMessageField('text')" style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); color:var(--success-color); font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">+ Texto</button>
                                    <button onclick="addQrMessageField('image')" style="background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); color:var(--primary-color); font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🖼 Img</button>
                                    <button onclick="addQrMessageField('video')" style="background:rgba(139,92,246,0.15); border:1px solid rgba(139,92,246,0.3); color:#a78bfa; font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🎬 Vid</button>
                                    <button onclick="addQrMessageField('audio')" style="background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.3); color:#fbbf24; font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🎵 Audio</button>
                                    <button onclick="addQrMessageField('action_label')" style="background:rgba(236,72,153,0.15); border:1px solid rgba(236,72,153,0.3); color:#ec4899; font-size:0.75rem; padding:0.3rem 0.6rem; border-radius:5px; font-weight:600; cursor:pointer;">🏷 Acci\u00f3n Tag</button>'''

if old_buttons in code:
    code = code.replace(old_buttons, new_buttons)
    print("Replaced buttons.")
else:
    print("Old buttons not found.")

# 2. Update addQrMessageField
old_add_start = '''                const typeColors = {text:'#10b981', image:'#3b82f6', video:'#8b5cf6', audio:'#f59e0b'};
                const typeIcons = {text:'📝', image:'🖼', video:'🎬', audio:'🎵'};
                const color = typeColors[type] || '#10b981';
                const icon = typeIcons[type] || '📝';'''

new_add_start = '''                const typeColors = {text:'#10b981', image:'#3b82f6', video:'#8b5cf6', audio:'#f59e0b', action_label:'#ec4899'};
                const typeIcons = {text:'📝', image:'🖼', video:'🎬', audio:'🎵', action_label:'🏷'};
                const color = typeColors[type] || '#10b981';
                const icon = typeIcons[type] || '📝';'''
                
if old_add_start in code:
    code = code.replace(old_add_start, new_add_start)
    print("Replaced typeColors.")

old_add_builder = '''                if(type === 'text') {
                    inner += `<textarea rows="2" class="qr-msg-input" style="width:100%; padding:0.5rem; border-radius:5px; border:1px solid var(--accent-border); background:var(--bg-main); color:var(--text-main); outline:none; font-size:0.85rem; resize:vertical; box-sizing:border-box;" placeholder="Escribe el mensaje...">${content}</textarea>`;
                } else {'''

new_add_builder = '''                if(type === 'text') {
                    inner += `<textarea rows="2" class="qr-msg-input" style="width:100%; padding:0.5rem; border-radius:5px; border:1px solid var(--accent-border); background:var(--bg-main); color:var(--text-main); outline:none; font-size:0.85rem; resize:vertical; box-sizing:border-box;" placeholder="Escribe el mensaje...">${content}</textarea>`;
                } else if(type === 'action_label') {
                    const selId = mediaId || '';
                    let opts = `<option value="">-- Seleccionar Etiqueta --</option>`;
                    (window._globalLabels||[]).forEach(l => {
                        opts += `<option value="${l.id}" ${l.id===selId?'selected':''}>${l.name}</option>`;
                    });
                    inner += `
                    <div style="display:flex; flex-direction:column; gap:0.4rem; padding:0.4rem; background:rgba(0,0,0,0.1); border-radius:6px; margin-top:0.3rem;">
                        <span style="font-size:0.8rem; color:var(--text-main); font-weight:600;">Acci\u00f3n Autom\u00e1tica: Poner/Quitar Etiqueta</span>
                        <span style="font-size:0.75rem; color:var(--text-muted); line-height:1.2;">Al ejecutarse este paso, la etiqueta seleccionada se a\u00f1adir\u00e1 al chat (o se quitar\u00e1 si ya existe).</span>
                        <select class="qr-action-select qr-media-id" style="width:100%; padding:0.6rem; border-radius:6px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); outline:none; font-size:0.85rem; cursor:pointer;">
                            ${opts}
                        </select>
                    </div>`;
                } else {'''

if old_add_builder in code:
    code = code.replace(old_add_builder, new_add_builder)
    print("Replaced add_builder.")
else:
    print("add_builder not found.")

# 3. Update preview inside list
old_preview_map = '''                        if(m.type === 'text') return m.content || '';
                        if(m.type === 'image') return '\\ud83d\\uddbc Imagen';
                        if(m.type === 'video') return '\\ud83c\\udfac Video';
                        if(m.type === 'audio') return '\\ud83c\\udfb5 Audio';
                        return '[media]';'''

new_preview_map = '''                        if(m.type === 'text') return m.content || '';
                        if(m.type === 'action_label') return '\\ud83c\\udff7 ' + (m.content || 'Tag');
                        if(m.type === 'image') return '\\ud83d\\uddbc Imagen';
                        if(m.type === 'video') return '\\ud83c\\udfac Video';
                        if(m.type === 'audio') return '\\ud83c\\udfb5 Audio';
                        return '[media]';'''
if old_preview_map in code:
    code = code.replace(old_preview_map, new_preview_map)
    print("Replaced preview.")

# 4. Update guardarNuevoQR extraction logic
old_guardar = '''                document.querySelectorAll('#qrMessagesContainer > div[data-msg-type]').forEach(block => {
                    const msgType = block.dataset.msgType;
                    if(msgType === 'text') {
                        const ta = block.querySelector('.qr-msg-input');
                        if(ta && ta.value.trim()) mensajes.push({type: 'text', content: ta.value.trim()});
                    } else {
                        const mediaId = block.querySelector('.qr-media-id')?.value?.trim();
                        const caption = block.querySelector('.qr-media-caption')?.value?.trim() || '';
                        if(mediaId) mensajes.push({type: msgType, media_id: mediaId, content: caption});
                    }
                });'''

new_guardar = '''                document.querySelectorAll('#qrMessagesContainer > div[data-msg-type]').forEach(block => {
                    const msgType = block.dataset.msgType;
                    if(msgType === 'text') {
                        const ta = block.querySelector('.qr-msg-input');
                        if(ta && ta.value.trim()) mensajes.push({type: 'text', content: ta.value.trim()});
                    } else if(msgType === 'action_label') {
                        const sel = block.querySelector('.qr-action-select');
                        if(sel && sel.value) mensajes.push({type: 'action_label', media_id: sel.value, content: sel.options[sel.selectedIndex].text});
                    } else {
                        const mediaId = block.querySelector('.qr-media-id')?.value?.trim();
                        const caption = block.querySelector('.qr-media-caption')?.value?.trim() || '';
                        if(mediaId) mensajes.push({type: msgType, media_id: mediaId, content: caption});
                    }
                });'''
if old_guardar in code:
    code = code.replace(old_guardar, new_guardar)
    print("Replaced guardar extract.")

open('server.py', 'w', encoding='utf-8').write(code)
print("All done.")

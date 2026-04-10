with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = '<button type="button" id="btnRecordAudio" style="background:var(--accent-bg); color:var(--text-main); border:none; border-radius:12px; height:44px; width:44px; display:flex; align-items:center; justify-content:center; cursor:pointer; margin-left: 0.5rem; margin-right: 0.5rem; transition: background 0.2s, color 0.2s;" title="Grabar nota de voz">'

replacement = '''<button type="button" id="btnCancelAudio" style="background:var(--danger-color); color:white; border:none; border-radius:12px; height:44px; width:44px; display:none; align-items:center; justify-content:center; cursor:pointer; margin-left: 0.5rem; transition: background 0.2s;" title="Cancelar grabación">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
                <button type="button" id="btnRecordAudio" style="background:var(--accent-bg); color:var(--text-main); border:none; border-radius:12px; height:44px; width:44px; display:flex; align-items:center; justify-content:center; cursor:pointer; margin-left: 0.5rem; margin-right: 0.5rem; transition: background 0.2s, color 0.2s;" title="Grabar nota de voz">'''

if target in text:
    text = text.replace(target, replacement)
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced successfully")
else:
    print("Not found")

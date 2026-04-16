> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `find_width.py` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Historial**: -                     // Marcar que este chat tiene historico completo cargado.
+                     // Historial completo cargado: el polling seguira pidiendo history=all
-                     // El polling lo usara para seguir pidiendo history=all indefinidamente,
+                     window._viewingAllHistory = true;
-                     // evitando que el chat vuelva a los 70 mensajes recientes.
+ 
-                     window._viewingAllHistory = true;
+                     // Limpiar param de URL sin recargar
- 
+                     const url = new URL(window.location);
-                     // Limpiar param de URL (sin recargar)
+                     url.searchParams.delete('msg_id');
-                     const url = new URL(window.location);
+                     window.history.replaceState({{}}, '', url);
-                     url.searchParams.delete('msg_id');
+ 
-                     window.history.replaceState({{}}, '', url);
+                     let attempts = 0;
- 
+                     function tryScroll() {{
-                     // Scroll con retry hasta encontrar el elemento
+                         const el = document.getElementById('msg-' + msgId);
-                     let attempts = 0;
+                         if (el) {{
-                     function tryScroll() {{
+                             requestAnimationFrame(() => requestAnimationFrame(() => {{
-                         const el = document.getElementById('msg-' + msgId);
+                                 // Scroll inicial (instant para evitar que smooth quede a medias)
-                         if (el) {{
+                                 el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
-                             requestAnimationFrame(() => requestAnimationFrame(() => {{
+ 
-                                 el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
+                                 // Highlight visual
-     
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Fixed null crash in Limpiar — fixes memory leak from uncleared timers**: -                     const initialTarget = document.getElementById('msg-' + msgId);
+                     // Limpiar param de URL de inmediato
-                     if (initialTarget) {{
+                     const url = new URL(window.location);
-                         window._isSearching = true;
+                     url.searchParams.delete('msg_id');
-                         
+                     window.history.replaceState({{}}, '', url);
-                         function pulseScroll(addStyle) {{
+ 
-                             const el = document.getElementById('msg-' + msgId);
+                     function highlightAndScroll(el) {{
-                             if (el) {{
+                         window._isSearching = true;
-                                 el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
+                         // Scroll instantaneo para la posicion inicial (no smooth, para no competir luego)
-                                 if (addStyle) {{
+                         el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
-                                     el.style.transition = 'all 0.5s ease';
+                         el.style.transition = 'all 0.5s ease';
-                                     el.style.boxShadow = '0 0 0 4px var(--primary-color)';
+                         el.style.boxShadow = '0 0 0 4px var(--primary-color)';
-                                     el.style.transform = 'scale(1.02)';
+                         el.style.transform = 'scale(1.02)';
-                                 }}
+ 
-                             }}
+                         // Re-anclar cuando las imagenes terminen de cargar (causan layout shift)
-                         }}
+                         const imgs = c.querySelectorAll('img');
-                         
+                         imgs.forEach(img => {{
-                         setTimeout(() => {{
+                             i
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Fixed null crash in Todas — parallelizes async operations for speed**: -     labels_filter_html = f"""
+     
-     <div style="position:relative; margin-top:1rem; text-align:left; display:flex; gap:0.5rem; align-items:center;">
+     active_line_name = "Todas las Líneas" if line_filter == "all" else aliases.get(line_filter, "Línea QR" if line_filter != "principal" else "Línea Principal")
-         <button type="button" onclick="const m = document.getElementById('inboxFilterMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:var(--text-main); font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600;">
+ 
-             <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
+     labels_filter_html = f"""
-             {active_label_name}
+     <div style="position:relative; margin-top:1rem; text-align:left; display:flex; gap:0.5rem; align-items:center;">
-         </button>
+         
-         
+         <button type="button" onclick="const m = document.getElementById('inboxLineMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:var(--text-main); font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600;">
-         <a href="{base_url}?tab={tab}&label={label_filter or ''}&unread={'false' if is_unread else 'true'}" style="background:{unread_btn_bg}; border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:{unread_btn_text}; font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600; text-decoration:none;">
+             <svg width="14" height="14" viewBox="0 0 24 24" fill=
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Optimized True — ensures atomic multi-step database operations**: -             "lineId": sesion_dict.get("lineId", "principal"),
+             "bot_activo": sesion_dict.get("bot_activo", True),
-             "bot_activo": sesion_dict.get("bot_activo", True),
+             "ultima_actividad": sesion_dict.get("ultima_actividad"), # datetime object
-             "ultima_actividad": sesion_dict.get("ultima_actividad"), # datetime object
+             "escalado_en": sesion_dict.get("escalado_en"),           # datetime object o None
-             "escalado_en": sesion_dict.get("escalado_en"),           # datetime object o None
+             "motivo_escalacion": sesion_dict.get("motivo_escalacion"),
-             "motivo_escalacion": sesion_dict.get("motivo_escalacion"),
+             "nombre_cliente": sesion_dict.get("nombre_cliente", "Cliente"),
-             "nombre_cliente": sesion_dict.get("nombre_cliente", "Cliente"),
+             "historial": sesion_dict.get("historial", []),
-             "historial": sesion_dict.get("historial", []),
+             "datos_pedido": sesion_dict.get("datos_pedido"),
-             "datos_pedido": sesion_dict.get("datos_pedido"),
+             "pedidos_multiples": sesion_dict.get("pedidos_multiples"),
-             "pedidos_multiples": sesion_dict.get("pedidos_multiples"),
+             "esperando_pedido_tester": sesion_dict.get("esperando_pedido_tester", False),
-             "esperando_pedido_tester": sesion_dict.get("esperando_pedido_tester", False),
+             "etiquetas": sesion_dict.get("etiquetas", []),
-             "etiquetas": sesion_dict.get("etiquetas", []),
+             "is_pinned": sesion_dict.get("is_pinned", False),
-             "is_pinned": sesion_dict.get("is_pinned", False),
+             "is_archived": sesion_dict.get("is_archived", False),
-             "is_archived": sesion_dict.get("is_archived", False),
+             "unread_count": sesion_dict.get("unread_count", 0),
-             "unread_count": sesion_dict.get("unread_count", 0),
+          
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [inicializar_firebase, _buscar, buscar_pedido_por_telefono, buscar_pedido_por_id, guardar_sesion_chat]
- **⚠️ GOTCHA: Patched security issue Restaurar — protects against XSS and CSRF token theft**: - import threading
+ @app.on_event("startup")
- import subprocess
+ def startup_event():
- import os
+     # ── Restaurar toda la memoria y stickers desde Firebase ──
- node_qr_process = None
+     try:
- 
+         from firebase_client import cargar_todas_las_sesiones
- def _run_node_magic():
+         # Restaurar sesiones (Inbox)
-     global node_qr_process
+         sesiones_restauradas = cargar_todas_las_sesiones()
-     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
+         for wa_id, s in sesiones_restauradas.items():
-     if os.path.exists(qr_dir):
+             sesiones[wa_id] = s
-         try:
+         print(f"[OK] Se restauraron {len(sesiones_restauradas)} conversaciones en memoria desde Firebase.")
-             node_exe = 'node'
+         
-             import platform
+         # Stickers are now loaded on-demand via Serverless Endpoints.
-             if platform.system() == 'Linux':
+         
-                 node_bin_dir = os.path.join(os.path.dirname(__file__), 'node_portable')
+         # Restaurar Etiquetas
-                 node_portable_exe = os.path.join(node_bin_dir, 'node-v20.12.2-linux-x64', 'bin', 'node')
+         from firebase_client import cargar_etiquetas_bd, cargar_grupos_bd
-                 if not os.path.exists(node_portable_exe):
+         global global_labels, global_groups
-                     try:
+         global_labels = cargar_etiquetas_bd()
-                         subprocess.run(['node', '-v'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
+         print(f"[OK] Se restauraron {len(global_labels)} etiquetas globales.")
-                     except (FileNotFoundError, Exception):
+         global_groups = cargar_grupos_bd()
-                         import urllib.request, tarfile
+         print(f"[OK] Se restauraron {len(global_groups)} grupos virtuales.")
-                         tar_path = os.path.join(os.path.dirname(__file__), 'node.tar.gz'
… [diff truncated]

### 📐 Generic Logic Conventions & Fixes
- **[what-changed] Replaced dependency Buscar**: - with open('server.py', encoding='utf-8') as f:
+ import ast
-     content = f.read()
+ 
- 
+ files_to_check = ['server.py', 'firebase_client.py', 'bot_atc.py', 'whatsapp_client.py']
- import re
+ 
- 
+ for fname in files_to_check:
- # Buscar patrones de f-string donde 'width' aparezca como variable Python
+     try:
- # (sin ser precedido por = o : que indicarian que es CSS/HTML)
+         with open(fname, encoding='utf-8') as f:
- lines = content.split('\n')
+             src = f.read()
- for i, line in enumerate(lines, 1):
+         # Buscar 'width' como nombre de variable en el AST
-     if 'width' not in line:
+         tree = ast.parse(src)
-         continue
+         for node in ast.walk(tree):
-     # Buscar {width} o {width: o {width,  (uso de variable en f-string)
+             if isinstance(node, ast.Name) and node.id == 'width':
-     matches = list(re.finditer(r'\{width[\}\s,:]', line))
+                 print(f'{fname}:{node.lineno}: Name(width) usado como variable')
-     for m in matches:
+             elif isinstance(node, ast.arg) and node.arg == 'width':
-         # Verificar que no sea CSS (dentro de string con ; alrededor)
+                 print(f'{fname}:{node.lineno}: arg(width) - parametro de funcion')
-         ctx = line[max(0,m.start()-20):m.end()+20]
+     except SyntaxError as e:
-         print(f'L{i}: ...{ctx}...')
+         print(f'{fname}: SyntaxError - {e}')
-         print(f'     Full: {line.strip()[:120]}')
+     except FileNotFoundError:
-         print()
+         pass

📌 IDE AST Context: Modified symbols likely include [files_to_check, src, tree]
- **[what-changed] Replaced dependency Buscar**: - import re
+ with open('server.py', encoding='utf-8') as f:
- 
+     content = f.read()
- with open('server.py', encoding='utf-8') as f:
+ 
-     content = f.read()
+ import re
- lines = content.split('\n')
+ # Buscar patrones de f-string donde 'width' aparezca como variable Python
- 
+ # (sin ser precedido por = o : que indicarian que es CSS/HTML)
- # Buscar donde se use 'width' como variable Python (asignacion o uso fuera de strings HTML)
+ lines = content.split('\n')
-     # Solo lineas Python (no HTML puro), que tengan 'width' como variable
+     if 'width' not in line:
-     s = line.strip()
+         continue
-     if not s or s.startswith('#'):
+     # Buscar {width} o {width: o {width,  (uso de variable en f-string)
-         continue
+     matches = list(re.finditer(r'\{width[\}\s,:]', line))
-     # Buscar patron de variable: width = o = width o (width) etc fuera de strings
+     for m in matches:
-     # Usando regex para encontrar word boundary
+         # Verificar que no sea CSS (dentro de string con ; alrededor)
-     matches = re.findall(r'\bwidth\b', s)
+         ctx = line[max(0,m.start()-20):m.end()+20]
-     if matches:
+         print(f'L{i}: ...{ctx}...')
-         # Excluir si es claramente HTML/CSS string entre comillas
+         print(f'     Full: {line.strip()[:120]}')
-         # Contar comillas antes del match
+         print()
-         idx = s.find('width')
+ 
-         before = s[:idx]
-         quote_count = before.count('"') + before.count("'")
-         if quote_count % 2 == 0:  # fuera de string
-             print(f'L{i}: {line.rstrip()[:140]}')
- 

📌 IDE AST Context: Modified symbols likely include [content, lines, matches, ctx]
- **[what-changed] Replaced dependency Buscar**: - import ast, sys
+ import re
- # Buscar lineas que use la variable 'width' sin definirla en scope inmediato
+ lines = content.split('\n')
- lines = content.split('\n')
+ 
- for i, line in enumerate(lines, 1):
+ # Buscar donde se use 'width' como variable Python (asignacion o uso fuera de strings HTML)
-     stripped = line.strip()
+ for i, line in enumerate(lines, 1):
-     # Buscar uso de `width` como variable de Python (no string)
+     # Solo lineas Python (no HTML puro), que tengan 'width' como variable
-     if (' width ' in stripped or stripped.startswith('width ') or '= width' in stripped or
+     s = line.strip()
-         'width)' in stripped or 'width,' in stripped or '(width' in stripped):
+     if not s or s.startswith('#'):
-         # Excluir strings y comentarios
+         continue
-         if '#' not in stripped[:stripped.find('width')] if 'width' in stripped else True:
+     # Buscar patron de variable: width = o = width o (width) etc fuera de strings
-             print(f'L{i}: {line.rstrip()[:130]}')
+     # Usando regex para encontrar word boundary
- 
+     matches = re.findall(r'\bwidth\b', s)
+     if matches:
+         # Excluir si es claramente HTML/CSS string entre comillas
+         # Contar comillas antes del match
+         idx = s.find('width')
+         before = s[:idx]
+         quote_count = before.count('"') + before.count("'")
+         if quote_count % 2 == 0:  # fuera de string
+             print(f'L{i}: {line.rstrip()[:140]}')
+ 

📌 IDE AST Context: Modified symbols likely include [content, lines, s, matches, idx]
- **[what-changed] what-changed in find_width.py**: - with open('server.py', encoding='utf-8') as f:
+ import ast, sys
-     lines = f.readlines()
+ 
- 
+ with open('server.py', encoding='utf-8') as f:
- for i, line in enumerate(lines, 1):
+     content = f.read()
-     if '{width}' in line or ('{width ' in line):
+ 
-         print(f'L{i}: {line.rstrip()[:150]}')
+ # Buscar lineas que use la variable 'width' sin definirla en scope inmediato
- 
+ lines = content.split('\n')
+ for i, line in enumerate(lines, 1):
+     stripped = line.strip()
+     # Buscar uso de `width` como variable de Python (no string)
+     if (' width ' in stripped or stripped.startswith('width ') or '= width' in stripped or
+         'width)' in stripped or 'width,' in stripped or '(width' in stripped):
+         # Excluir strings y comentarios
+         if '#' not in stripped[:stripped.find('width')] if 'width' in stripped else True:
+             print(f'L{i}: {line.rstrip()[:130]}')
+ 

📌 IDE AST Context: Modified symbols likely include [content, lines, stripped]
- **[what-changed] 🟢 Edited admin.html (41 changes, 107min)**: Active editing session on admin.html.
41 content changes over 107 minutes.
- **[problem-fix] Fixed null crash in Marcar**: -                     // Limpiar param de URL de inmediato
+                     // Marcar que este chat tiene historico completo cargado.
-                     const url = new URL(window.location);
+                     // El polling lo usara para seguir pidiendo history=all indefinidamente,
-                     url.searchParams.delete('msg_id');
+                     // evitando que el chat vuelva a los 70 mensajes recientes.
-                     window.history.replaceState({{}}, '', url);
+                     window._viewingAllHistory = true;
-                     function highlightAndScroll(el) {{
+                     // Limpiar param de URL (sin recargar)
-                         window._isSearching = true;
+                     const url = new URL(window.location);
-                         // Scroll instantaneo para la posicion inicial (no smooth, para no competir luego)
+                     url.searchParams.delete('msg_id');
-                         el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
+                     window.history.replaceState({{}}, '', url);
-                         el.style.transition = 'all 0.5s ease';
+ 
-                         el.style.boxShadow = '0 0 0 4px var(--primary-color)';
+                     // Scroll con retry hasta encontrar el elemento
-                         el.style.transform = 'scale(1.02)';
+                     let attempts = 0;
- 
+                     function tryScroll() {{
-                         // Re-anclar cuando las imagenes terminen de cargar (causan layout shift)
+                         const el = document.getElementById('msg-' + msgId);
-                         const imgs = c.querySelectorAll('img');
+                         if (el) {{
-                         imgs.forEach(img => {{
+                             requestAnimationFrame(() => requestAnimationFrame(() => {{
-                             if (!img.complete) {{
+                   
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[convention] Fixed null crash in DOCTYPE — wraps unsafe operation in error boundary — confirmed 3x**: - <!DOCTYPE html>
+ <!DOCTYPE html>
- <html lang="es">
+ <html lang="es">
- 
+ 
- <head>
+ <head>
-     <meta charset="UTF-8">
+     <meta charset="UTF-8">
-     <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
+     <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
-     <title>Configuración de Agente IA - IA-ATC</title>
+     <title>Configuración de Agente IA - IA-ATC</title>
-     <!-- Fuentes de Google -->
+     <!-- Fuentes de Google -->
-     <link
+     <link
-         href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
+         href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
-         rel="stylesheet">
+         rel="stylesheet">
-     <style>
+     <style>
-         :root {
+         :root {
-             /* 1. Nivel de Color Principal */
+             /* 1. Nivel de Color Principal */
-             --primary-color: #717f7f;
+             --primary-color: #717f7f;
-             --primary-hover: #2563eb;
+             --primary-hover: #2563eb;
-             /* 2. Nivel de Color de Acento */
+             /* 2. Nivel de Color de Acento */
-             --accent-bg: #1e293b;
+             --accent-bg: #1e293b;
-             --accent-border: #334155;
+             --accent-border: #334155;
-             --accent-hover-soft: #334155;
+             --accent-hover-soft: #334155;
-             /* 3. Nivel de Color de Fondo General */
+             /* 3. Nivel de Color de Fondo General */
-             --bg-main: #0f172a;
+             --bg-main: #0f172a;
-             /* 4. Tipografías */
+             /* 4. Tipografías */
-             --font-main: 'Inter', sans-serif;
+             --font-main: 'Inter', sans-serif;
-           
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in whatsapp_client.py**: -         req = urllib.request.Request("http://127.0.0.1:3000/api/qr/send", 
+         req = urllib.request.Request("http://localhost:3000/api/qr/send", 
-         req = urllib.request.Request("http://127.0.0.1:3000/api/qr/send", 
+         req = urllib.request.Request("http://localhost:3000/api/qr/send", 
- 
+ 
- 
- **[convention] Fixed null crash in Limpiar — confirmed 3x**: - # ====================[REDACTED]
+ ﻿# ====================[REDACTED]
-                     const initialTarget = document.getElementById('msg-' + msgId);
+                     // Limpiar param de URL de inmediato
-                     if (initialTarget) {{
+                     const url = new URL(window.location);
-                         window._isSearching = true;
+                     url.searchParams.delete('msg_id');
-                         
+                     window.history.replaceState({{}}, '', url);
-                         function pulseScroll(addStyle) {{
+ 
-                             const el = document.getElementById('msg-' + msgId);
+                     function highlightAndScroll(el) {{
-                             if (el) {{
+                         window._isSearching = true;
-                                 el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
+                         el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
-                                 if (addStyle) {{
+                         el.style.transition = 'all 0.5s ease';
-                                     el.style.transition = 'all 0.5s ease';
+                         el.style.boxShadow = '0 0 0 4px var(--primary-color)';
-                                     el.style.boxShadow = '0 0 0 4px var(--primary-color)';
+                         el.style.transform = 'scale(1.02)';
-                                     el.style.transform = 'scale(1.02)';
+                         setTimeout(() => el.scrollIntoView({{ behavior: 'smooth', block: 'center' }}), 600);
-                                 }}
+                         setTimeout(() => el.scrollIntoView({{ behavior: 'smooth', block: 'center' }}), 1200);
-                             }}
+                         setTimeout(() => {{
-                         }}
+                             el.s
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, node_qr_process]
- **[convention] problem-fix in server.py — confirmed 7x**: - ﻿# ====================[REDACTED]
+ # ====================[REDACTED]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, node_qr_process]

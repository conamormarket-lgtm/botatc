import os
import re

css = """        /* ---------------- LEFT SIDEBAR ---------------- */
        .sidebar-nav {
            width: 55px; /* Was 70px */
            background-color: var(--bg-sidebar, var(--bg-main));
            border-right: 1px solid var(--accent-border);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 1.5rem 0;
            z-index: 10;
        }
        .nav-item {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            margin-bottom: 1rem;
            transition: all 0.2s ease;
            text-decoration: none;
        }
        .nav-item:hover {
            color: var(--text-main);
            background-color: var(--bg-hover, rgba(255,255,255,0.05));
        }
        .nav-item.active {
            color: var(--primary-color);
            background-color: rgba(59, 130, 246, 0.1);
        }
        .nav-item svg {
            width: 20px;
            height: 20px;
            fill: none;
            stroke: currentColor;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }"""

media_css = """            .sidebar-nav {
                flex-direction: row;
                width: 100%;
                height: 65px;
                padding: 0;
                border-right: none;
                border-top: 1px solid var(--accent-border);
                order: 3;
                justify-content: space-around;
                background-color: var(--bg-sidebar, var(--bg-main));
            }
            .nav-item { margin-bottom: 0; }
            body.view-chat .sidebar-nav { display: none !important; }"""

html_nav = """    <nav class="sidebar-nav">
        <a href="/inbox" class="nav-item {inbox_active}" title="Bandeja de Entrada (Inbox)">
            <svg viewBox="0 0 24 24"><path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>
        </a>
        <a href="/settings" class="nav-item {settings_active}" title="Personalizar Agente IA">
            <svg viewBox="0 0 24 24"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
        </a>
        <a href="/usuarios" class="nav-item {usuarios_active}" title="Panel de Usuarios">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
        </a>
        <a href="/admin" class="nav-item {admin_active}" title="Panel Clásico Anterior">
            <svg viewBox="0 0 24 24"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>
        </a>
        
        <div style="flex:1;"></div>
        
        <a href="/perfil" class="nav-item {perfil_active}" title="Mi Perfil" style="margin-bottom: 5px; color: var(--text-muted); display: flex; justify-content: center; text-decoration: none;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 24px; height: 24px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        </a>
        <a href="/logout" class="nav-item" title="Cerrar Sesión" style="color: #ef4444; margin-bottom: 10px; display: flex; justify-content: center; text-decoration: none;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 26px; height: 26px; opacity: 0.8; transition: opacity 0.2s;"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
        </a>
    </nav>"""

def replace_file(filepath, active_tab):
    with open(filepath, "r", encoding="utf-8") as f: content = f.read()

    # Desktop CSS replacement
    content = re.sub(r'/\*\s*-*\s*LEFT SIDEBAR\s*-*\s*\*/.*?(?=\s*\/\*|\s*\.chat-list-panel|\s*@media)', css, content, flags=re.DOTALL)
    content = re.sub(r'/\*\s*-*\s*SIDEBAR NAV\s*-*\s*\*/.*?\.nav-item\s*svg\s*\{.*?\}', css, content, flags=re.DOTALL)

    # Clean any remnant .spacer 
    content = re.sub(r'\.spacer\s*\{.*?\}', '', content, flags=re.DOTALL)

    # Mobile CSS replacement
    content = re.sub(r'\.sidebar-nav\s*\{\s*flex-direction:\s*row;.*?\}\s*(?:\.spacer\s*\{.*?\})?\s*(?:\.nav-item\s*\{.*?\})?(?:\s*body\.view-chat\s*\.sidebar-nav\s*\{.*?\})?', media_css, content, count=1, flags=re.DOTALL)

    # HTML substitution
    current_nav = html_nav
    current_nav = current_nav.replace("{inbox_active}", "active" if active_tab=="inbox" else "")
    current_nav = current_nav.replace("{settings_active}", "active" if active_tab=="settings" else "")
    current_nav = current_nav.replace("{usuarios_active}", "active" if active_tab=="usuarios" else "")
    current_nav = current_nav.replace("{admin_active}", "active" if active_tab=="admin" else "")
    current_nav = current_nav.replace("{perfil_active}", "active" if active_tab=="perfil" else "")
    
    # We must match <nav class="sidebar-nav">... up to </nav>
    content = re.sub(r'<nav class="sidebar-nav">.*?</nav>', current_nav, content, flags=re.DOTALL)

    # also remove any remnant {admin_button} or {settings_button} outside <nav>
    content = content.replace("{admin_button}", "")
    content = content.replace("{settings_button}", "")

    with open(filepath, "w", encoding="utf-8") as f: f.write(content)
    print(f"File {filepath} updated successfully.")

replace_file("inbox.html", "inbox")
replace_file("settings.html", "settings")
replace_file("perfil.html", "perfil")

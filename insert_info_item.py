import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open("inbox.html", "r", encoding="utf-8") as f:
    html = f.read()

# Target: "Copiar Texto\n        </div>\n    </div>" — the last ctx-item closes and then the menu div closes
# Insert info item between the two </div>s

info_item = """
        <div class="ctx-item" id="ctxMsgInfo"
            style="padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; border-top:1px solid var(--accent-border); color:var(--text-main); display:none; align-items:center; gap:0.5rem; transition:background 0.2s;"
            onmouseover="this.style.background='var(--accent-bg)'" onmouseout="this.style.background=''">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <strong>Información</strong>
        </div>"""

# Insert before the menu closing </div>
target = "            Copiar Texto\n        </div>\n    </div>"
replacement = "            Copiar Texto\n        </div>" + info_item + "\n    </div>"
if target in html:
    html = html.replace(target, replacement, 1)
    print("Inserted Información item in existing menu")
else:
    print("Target not found, trying alternative...")
    target2 = "            Copiar Texto\r\n        </div>\r\n    </div>"
    replacement2 = "            Copiar Texto\r\n        </div>" + info_item + "\r\n    </div>"
    if target2 in html:
        html = html.replace(target2, replacement2, 1)
        print("Inserted (CRLF version)")
    else:
        # Try to find just the general pattern
        m = re.search(r'Copiar Texto\s*</div>\s*</div>', html)
        if m:
            html = html[:m.end()-6] + info_item + html[m.end()-6:]
            print("Inserted via regex")
        else:
            print("FAILED to find insertion point")

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(html)

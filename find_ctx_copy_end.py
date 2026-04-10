import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open("inbox.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find the ctxCopy div (last item "Copiar Texto") and insert Información after it
idx = html.find('class="ctx-item" id="ctxCopy"')
if idx == -1:
    print("ctxCopy not found")
else:
    # Find closing </div> of this item
    close_div = html.find('</div>', idx)
    # Make sure we get the right end (the item's own closing div)
    # Peek at what's there
    print("Closing context:")
    print(html[close_div-50:close_div+200])

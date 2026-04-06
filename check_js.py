import subprocess
import os

with open('check_syntax.js', 'w', encoding='utf-8') as f:
    # Just extract <script> blocks and try to node them
    with open('inbox.html', 'r', encoding='utf-8') as html:
        content = html.read()
        
    scripts = []
    import re
    # simple extraction
    blocks = re.findall(r'<script.*?>\s*(.*?)\s*</script>', content, re.DOTALL)
    for i, b in enumerate(blocks):
        try:
            with open(f'tmp_s_{i}.js', 'w', encoding='utf-8') as out:
                out.write(b)
            r = subprocess.run(['node', f'tmp_s_{i}.js', '--check'], capture_output=True, text=True)
            if r.returncode != 0:
                print(f"Script {i} syntax error:\n{r.stderr}")
        except:
            pass

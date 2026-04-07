import re
import subprocess
import os

with open("inbox.html", "r", encoding="utf-8") as f:
    content = f.read()

scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
for i, script in enumerate(scripts):
    with open(f"tmp_{i}.js", "w", encoding="utf-8") as out:
        out.write(script)
    r = subprocess.run(["node", "-c", f"tmp_{i}.js"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"--- Syntax error in script {i} ---")
        print(r.stderr)
        # print the problematic lines
        lines = script.split('\n')
        for idx, l in enumerate(lines):
            print(f"{idx+1}: {l}")
    os.remove(f"tmp_{i}.js")

print("Done checking syntax.")

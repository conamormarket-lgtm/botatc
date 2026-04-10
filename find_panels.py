import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()

print("Panels in inbox.html:")
for line in s.split('\n'):
    if 'id="' in line and '"panel' in line:
        print(line.strip())
print("\nLabels:")
for line in s.split('\n'):
    if 'Labels' in line or 'Etiqueta' in line or 'Grupos' in line:
        print(line.strip()[:150])

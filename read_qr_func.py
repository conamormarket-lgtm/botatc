import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('async function cargarQuickReplies')
idx2 = text.find('</script>', idx)

print(text[idx:idx+1500])

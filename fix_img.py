import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target_img = 'style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: inline-block; cursor: zoom-in;"'
rep_img = 'style="max-width: 100%; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;"'

if target_img in text:
    text = text.replace(target_img, rep_img)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed image css")
else:
    print("Image target not found.")

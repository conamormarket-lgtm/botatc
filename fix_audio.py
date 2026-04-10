import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target_audio = """elif tipo == "audio":
                    return f'<div style="text-align:center;"><audio controls src="{src_url}" style="width: 100%; max-width: 250px; height: 40px; outline: none; margin-bottom: 5px; box-sizing: border-box; display: block;"></audio></div>'"""

rep_audio = """elif tipo == "audio":
                    return f'<div style="min-width: 250px; max-width: 100%; margin: 0 auto; display: flex;"><audio controls src="{src_url}" style="width: 100%; height: 45px; outline: none; margin-bottom: 5px; border-radius: 20px;"></audio></div>'"""

if target_audio in text:
    text = text.replace(target_audio, rep_audio)
    print("Replaced AUDIO")
else:
    print("Audio target not found!")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

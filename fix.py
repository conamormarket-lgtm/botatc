with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'try:' in line and 'import urllib.parse' in lines[i+1]:
        out.append('            import urllib.parse\n')
        i += 2 # skip try and import
        continue
    if 'elif match_audio:' in line:
        out.append('            elif match_audio:\n')
        out.append('                w_id_current = enviar_media(wa_id, "audio", match_audio.group(1), reply_to_wamid)\n')
        i += 2 # skip elif and the incorrectly indented next line
        continue
    out.append(line)
    i += 1

with open('server.py', 'w', encoding='utf-8') as f:
    f.writelines(out)

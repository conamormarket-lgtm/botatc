import re
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

old_ff = '''                tmp_out_name = tmp_in_name.replace(".webm", ".ogg")
                
                # Ejecutar FFMPEG (disponible via Aptfile en Railway)
                # WhatsApp RECOMIENDA audio/ogg; codecs=opus para notas de voz perfectas
                result = subprocess.run([
                    'ffmpeg', '-y', '-i', tmp_in_name,
                    '-c:a', 'libopus', '-b:a', '32k',
                    '-vbr', 'on', '-compression_level', '10',
                    tmp_out_name
                ], capture_output=True)
                
                if result.returncode == 0 and os.path.exists(tmp_out_name):
                    with open(tmp_out_name, "rb") as f_out:
                        content = f_out.read()
                    final_mime = "audio/ogg; codecs=opus"
                    fallback_name = "voice_note.ogg"
                else:
                    print("FFMPEG fallback ignorado o error:", result.stderr.decode('utf-8', 'ignore'))
                    # Fallback si no hay ffmpeg: Meta API a veces acepta MP4 audio crudo
                    final_mime = "audio/mp4" 
                    fallback_name = "voice_note.mp4"'''

new_ff = '''                tmp_out_name = tmp_in_name.replace(".webm", ".mp4")
                
                # Ejecutar FFMPEG (disponible via Aptfile en Railway)
                # Utiliza codec aac compatible universal con .mp4
                result = subprocess.run([
                    'ffmpeg', '-y', '-i', tmp_in_name,
                    '-c:a', 'aac', '-b:a', '64k',
                    tmp_out_name
                ], capture_output=True)
                
                if result.returncode == 0 and os.path.exists(tmp_out_name):
                    with open(tmp_out_name, "rb") as f_out:
                        content = f_out.read()
                    final_mime = "audio/mp4"
                    fallback_name = "voice.mp4"
                else:
                    print("FFMPEG error detallado:", result.stderr.decode('utf-8', 'ignore') if result.stderr else "N/A")
                    final_mime = "audio/mp4" 
                    fallback_name = "voice.mp4"'''

if 'libopus' in text:
    text = text.replace(old_ff, new_ff)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced libopus with aac for mp4")
else:
    print("libopus absent")

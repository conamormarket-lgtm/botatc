import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

old_code = """        # Conversion nativa WebM -> OGG para WhatsApp Voice Notes
        if "webm" in final_mime.lower() or "audio" in final_mime.lower():
            import subprocess, os, tempfile
            try:
                # Usar tmp para cross-platform compatibility
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_in:
                    tmp_in.write(content)
                    tmp_in_name = tmp_in.name
                tmp_out_name = tmp_in_name.replace(".webm", ".mp4")

                # Ejecutar FFMPEG (disponible via Aptfile en Railway)
                # Utiliza codec aac compatible universal con .mp4
                result = subprocess.run([
                    'ffmpeg', '-y', '-i', tmp_in_name,
                    '-c:a', 'aac', '-b:a', '64k',
                    tmp_out_name
                ], capture_output=True)"""

new_code = """        # Conversion nativa WebM -> MP4 para WhatsApp Voice Notes
        if "webm" in final_mime.lower() or "audio" in final_mime.lower():
            import subprocess, os, tempfile
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            try:
                # Usar tmp para cross-platform compatibility
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_in:
                    tmp_in.write(content)
                    tmp_in_name = tmp_in.name
                tmp_out_name = tmp_in_name.replace(".webm", ".mp4")

                # Ejecutar FFMPEG (via imageio-ffmpeg PIP)
                result = subprocess.run([
                    ffmpeg_exe, '-y', '-i', tmp_in_name,
                    '-c:a', 'aac', '-b:a', '64k',
                    tmp_out_name
                ], capture_output=True)"""
text = text.replace(old_code, new_code)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated ffmpeg call")

import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

new_block = """# Conversion nativa WebM -> MP4 para WhatsApp Voice Notes
        if "webm" in final_mime.lower():
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

text = re.sub(r'# Conversion nativa WebM.*?capture_output=True\)', new_block, text, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated via re.sub successfully")

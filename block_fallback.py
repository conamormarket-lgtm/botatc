import re
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

old_ff = '''                if result.returncode == 0 and os.path.exists(tmp_out_name):
                    with open(tmp_out_name, "rb") as f_out:
                        content = f_out.read()
                    final_mime = "audio/mp4"
                    fallback_name = "voice.mp4"
                else:
                    print("FFMPEG error detallado:", result.stderr.decode('utf-8', 'ignore') if result.stderr else "N/A")
                    final_mime = "audio/mp4" 
                    fallback_name = "voice.mp4"
                    
                os.remove(tmp_in_name)
                if os.path.exists(tmp_out_name): os.remove(tmp_out_name)
            except Exception as ex:
                print(f"Error procesando audio con ffmpeg: {ex}")
                final_mime = "audio/mp4"'''

new_ff = '''                if result.returncode == 0 and os.path.exists(tmp_out_name):
                    with open(tmp_out_name, "rb") as f_out:
                        content = f_out.read()
                    final_mime = "audio/mp4"
                    fallback_name = "voice.mp4"
                else:
                    err_msg = result.stderr.decode('utf-8', 'ignore') if result.stderr else "ExitCode!=0"
                    print("FFMPEG fallback ignorado o error:", err_msg)
                    return {"ok": False, "error": f"FFMPEG Conversion Failed: {err_msg}"}
                    
                os.remove(tmp_in_name)
                if os.path.exists(tmp_out_name): os.remove(tmp_out_name)
            except Exception as ex:
                print(f"Error procesando audio con ffmpeg: {ex}")
                return {"ok": False, "error": f"FFMPEG Missing on server: {ex}"}'''

if 'FFMPEG Missing' not in text:
    text = text.replace(old_ff, new_ff)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Block FFMPEG fallback")

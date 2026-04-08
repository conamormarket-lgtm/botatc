import re
with open("inbox.html", "r", encoding="utf-8") as f:
    inbox_text = f.read()

# Fix 1: Remove && !isPhoneNum from search
old_search_logic = "if(val.length >= 3 && !isPhoneNum) {"
new_search_logic = "if(val.length >= 3) {"
inbox_text = inbox_text.replace(old_search_logic, new_search_logic)

# Fix 2: Improve error handling for Microphone API
old_err_logic = '''                    } catch(err) {
                        alert("Es necesario otorgar permisos de micrófono al navegador para grabar audios.");
                    }'''
new_err_logic = '''                    } catch(err) {
                        console.error('Audio Recorder Error:', err);
                        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                            alert("❌ ¡Conexión Insegura! Tu navegador ha bloqueado el micrófono por seguridad. Las web de grabación de audio OBLIGAN a que uses 'https://' o entres desde 'http://localhost' en lugar de usar una IP directa de la red.");
                        } else {
                            alert("Permiso Denegado o Error: " + err.message + ". Verifica el candadito arriba a la izquierda y dale permisos al micrófono.");
                        }
                    }'''
inbox_text = inbox_text.replace(old_err_logic, new_err_logic)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(inbox_text)

print("Fixed search bug and improved audio recording error messaging")

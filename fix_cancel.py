import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""                if (btnRecord) {
                    btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0"""

rep = r"""                if (btnRecord) {
                    isRecording = false;
                    window._isAudioRecording = false;
                    if(window.toggleSendMicButton) window.toggleSendMicButton();
                    btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0"""

if target in text:
    text = text.replace(target, rep)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed cancel")
else:
    print("Cancel logic target not found")

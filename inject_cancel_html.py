import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# Modify `isRecording` start to show the cancel button
target1 = r"""                        mediaRecorder.start();
                        isRecording = true;
                        
                        btnRecord.style.background = "#ef4444";"""
replace1 = r"""                        mediaRecorder.start();
                        mediaRecorder.canceled = false;
                        isRecording = true;
                        if(document.getElementById('btnCancelAudio')) document.getElementById('btnCancelAudio').style.display = 'flex';
                        
                        btnRecord.style.background = "#ef4444";"""

text = text.replace(target1, replace1)

# Modify `isRecording` stop to hide the cancel button
target2 = r"""                    btnRecord.style.background = "var(--accent-bg)";
                    btnRecord.style.color = "var(--text-main)";"""
replace2 = r"""                    btnRecord.style.background = "var(--accent-bg)";
                    btnRecord.style.color = "var(--text-main)";
                    if(document.getElementById('btnCancelAudio')) document.getElementById('btnCancelAudio').style.display = 'none';"""

text = text.replace(target2, replace2)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

print("success")

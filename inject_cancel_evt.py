import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

cancel_logic = r"""
        document.addEventListener('click', async function(e) {
            const btnCancel = e.target.closest('#btnCancelAudio');
            if(btnCancel && isRecording) {
                mediaRecorder.canceled = true; // flag ignored by 'stop' listener!
                mediaRecorder.stop();
                isRecording = false;
                mediaRecorder.stream.getTracks().forEach(t => t.stop());
                
                const btnRecord = document.getElementById('btnRecordAudio');
                btnRecord.style.background = "var(--accent-bg)";
                btnRecord.style.color = "var(--text-main)";
                btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
                btnCancel.style.display = 'none';
                
                const manualInput = document.getElementById("manualMsgInput");
                if(manualInput && manualInput.dataset.originalPlaceholder) {
                    manualInput.placeholder = manualInput.dataset.originalPlaceholder;
                }
            }
        });
"""

if 'mediaRecorder.canceled = true' not in text:
    text = text.replace("document.addEventListener('click', async function(e) {", cancel_logic + "\n        document.addEventListener('click', async function(e) {")
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected event listener")
else:
    print("Already there")

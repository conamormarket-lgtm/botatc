import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update stop event listener to check `mediaRecorder.canceled`
target1 = r"""                        mediaRecorder.addEventListener("stop", async () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // WebM/OGG format for audio
                            const formData = new FormData();"""
replace1 = r"""                        mediaRecorder.addEventListener("stop", async () => {
                            if (mediaRecorder.canceled) {
                                return; // Do not send audio if canceled
                            }
                            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // WebM/OGG format for audio
                            const formData = new FormData();"""
text = text.replace(target1, replace1)

# 2. Update mediaRecorder.start() logic
target2 = r"""                        mediaRecorder.start();
                        btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>`;
                        btnRecord.style.color = "var(--danger-color)";
                    } catch (err) {"""
replace2 = r"""                        mediaRecorder.start();
                        mediaRecorder.canceled = false;
                        btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>`;
                        btnRecord.style.color = "var(--danger-color)";
                        if(document.getElementById('btnCancelAudio')) document.getElementById('btnCancelAudio').style.display = 'flex';
                    } catch (err) {"""
text = text.replace(target2, replace2)

# 3. Update mediaRecorder.stop() logic for NORMAL SEND
target3 = r"""                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(t => t.stop()); // close microphone
                    btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
                    btnRecord.style.color = "var(--text-main)";
                } else {"""
replace3 = r"""                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(t => t.stop()); // close microphone
                    btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
                    btnRecord.style.color = "var(--text-main)";
                    if(document.getElementById('btnCancelAudio')) document.getElementById('btnCancelAudio').style.display = 'none';
                } else {"""
text = text.replace(target3, replace3)

# 4. Add the cancel button click listener explicitly
cancel_listener = r"""
        document.body.addEventListener('click', async (e) => {
            const btnCancel = e.target.closest('#btnCancelAudio');
            if (btnCancel && typeof mediaRecorder !== 'undefined' && mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.canceled = true; // sets custom flag so the 'stop' event ignores it
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(t => t.stop()); // close microphone
                
                const btnRecord = document.getElementById('btnRecordAudio');
                if (btnRecord) {
                    btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
                    btnRecord.style.color = "var(--text-main)";
                }
                btnCancel.style.display = 'none';
            }
        });
    </script>
</body>"""
if 'btnCancelAudio' not in text:
    pass
if 'mediaRecorder.canceled = true;' not in text:
    text = text.replace("</script>\n</body>", cancel_listener)


with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

print(f"Replaced successfully {target2 in text}")

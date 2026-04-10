import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""        // Alternar boton enviar / grabar audio
        window.toggleSendMicButton = function() {
            const input = document.getElementById('manualMsgInput');
            const submitMenu = document.getElementById('btnSubmitForm');
            const micMenu = document.getElementById('btnRecordAudio');
            if (input && submitMenu && micMenu) {
                if (input.value.trim().length > 0) {
                    submitMenu.style.display = 'flex';
                    micMenu.style.display = 'none';
                } else {
                    submitMenu.style.display = 'none';
                    micMenu.style.display = 'flex';
                }
            }
        };"""

rep = r"""        // Alternar boton enviar / grabar audio
        window.toggleSendMicButton = function() {
            if (window._isAudioRecording) return; // No alternar si estamos grabando
            const input = document.getElementById('manualMsgInput');
            const submitMenu = document.getElementById('btnSubmitForm');
            const micMenu = document.getElementById('btnRecordAudio');
            if (input && submitMenu && micMenu) {
                if (input.value.trim().length > 0) {
                    submitMenu.style.display = 'flex';
                    micMenu.style.display = 'none';
                } else {
                    submitMenu.style.display = 'none';
                    micMenu.style.display = 'flex';
                }
            }
        };"""

if target in text:
    text = text.replace(target, rep)
else:
    print("ToggleSendMic target not found")

# Now inject window._isAudioRecording into the recording logic
record_target = r"""        let isRecording = false;"""
record_rep = r"""        let isRecording = false;
        window._isAudioRecording = false;"""

if record_target in text:
    text = text.replace(record_target, record_rep)

# Iniciar
start_target = r"""                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);"""
start_rep = r"""                    try {
                        window._isAudioRecording = true;
                        if(window.toggleSendMicButton) window.toggleSendMicButton();
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);"""
if start_target in text:
    text = text.replace(start_target, start_rep)

# Parar
stop_target = r"""                    isRecording = false;
                    clearInterval(audioTimer);"""
stop_rep = r"""                    isRecording = false;
                    window._isAudioRecording = false;
                    clearInterval(audioTimer);
                    document.getElementById('manualMsgInput').value = '';
                    if(window.toggleSendMicButton) window.toggleSendMicButton();"""
if stop_target in text:
    text = text.replace(stop_target, stop_rep)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed audio recording toggle conflict")

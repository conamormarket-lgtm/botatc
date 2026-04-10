import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = "// UTILITARIO: Alternar botón Grabar/Enviar"
rep = """// UTILITARIO: Formato de tiempo para Audios
        window.formatAudioTime = function(seconds) {
            if (!seconds || isNaN(seconds)) return "0:00";
            const min = Math.floor(seconds / 60);
            const sec = Math.floor(seconds % 60);
            return min + ":" + (sec < 10 ? "0" : "") + sec;
        };

        window._currentAudio = null;
        window._currentBtn = null;
        window.toggleAudio = function(btn) {
            const container = btn.closest('.custom-audio-player');
            const audio = container.querySelector('audio');
            const iconPlay = btn.querySelector('.icon-play');
            const iconPause = btn.querySelector('.icon-pause');

            if (window._currentAudio && window._currentAudio !== audio) {
                window._currentAudio.pause();
                if (window._currentBtn) {
                    window._currentBtn.querySelector('.icon-play').style.display = 'block';
                    window._currentBtn.querySelector('.icon-pause').style.display = 'none';
                }
            }

            if (audio.paused) {
                audio.play();
                iconPlay.style.display = 'none';
                iconPause.style.display = 'block';
                window._currentAudio = audio;
                window._currentBtn = btn;
            } else {
                audio.pause();
                iconPlay.style.display = 'block';
                iconPause.style.display = 'none';
            }
        };

        window.seekAudio = function(e, timeline) {
            const container = timeline.closest('.custom-audio-player');
            const audio = container.querySelector('audio');
            if(!audio.duration || isNaN(audio.duration)) return;
            const rect = timeline.getBoundingClientRect();
            const percent = Math.min(Math.max((e.clientX - rect.left) / rect.width, 0), 1);
            audio.currentTime = percent * audio.duration;
            // Immediate UI update
            container.querySelector('.cap-progress').style.width = (percent * 100) + '%';
            container.querySelector('.cap-time').textContent = window.formatAudioTime(audio.currentTime);
        };

        // UTILITARIO: Alternar botón Grabar/Enviar"""

if target in text:
    text = text.replace(target, rep)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected JS for Audio")
else:
    print("JS Target not found")

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target_audio = """elif tipo == "audio":
                    return f'<div style="min-width: 250px; max-width: 100%; margin: 0 auto; display: flex;"><audio controls src="{src_url}" style="width: 100%; height: 45px; outline: none; margin-bottom: 5px; border-radius: 20px;"></audio></div>'"""

rep_audio = """elif tipo == "audio":
                    return f\"\"\"<div class="custom-audio-player" style="display:flex; align-items:center; gap:0.6rem; width:100%; min-width:200px; max-width:300px; margin: 5px 0;">
                        <audio src="{src_url}" preload="metadata" style="display:none;" 
                            onloadedmetadata="this.parentElement.querySelector('.cap-time').textContent = window.formatAudioTime(this.duration);" 
                            ontimeupdate="this.parentElement.querySelector('.cap-progress').style.width = (this.currentTime / this.duration * 100) + '%'; this.parentElement.querySelector('.cap-time').textContent = window.formatAudioTime(this.currentTime);" 
                            onended="this.parentElement.querySelector('.icon-play').style.display='block'; this.parentElement.querySelector('.icon-pause').style.display='none'; this.currentTime=0; this.parentElement.querySelector('.cap-progress').style.width='0%'; this.parentElement.querySelector('.cap-time').textContent = window.formatAudioTime(this.duration);">
                        </audio>
                        <button class="cap-play-btn" type="button" onclick="window.toggleAudio(this)" style="background:var(--primary-color); color:white; border:none; border-radius:50%; width:38px; height:38px; display:flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0; box-shadow:0 2px 4px rgba(0,0,0,0.2); transition:transform 0.1s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                            <svg class="icon-play" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-left:2px;"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                            <svg class="icon-pause" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="display:none;"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
                        </button>
                        <div class="cap-timeline" onclick="window.seekAudio(event, this)" style="flex:1; height:6px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:4px; cursor:pointer; position:relative; overflow:hidden;">
                            <div class="cap-progress" style="width:0%; height:100%; background:var(--primary-color); position:absolute; left:0; top:0; pointer-events:none; transition: width 0.1s linear;"></div>
                        </div>
                        <span class="cap-time" style="font-size:0.75rem; color:inherit; opacity:0.8; font-weight:500; min-width:35px; text-align:right; font-family:var(--font-main);">0:00</span>
                    </div>\"\"\""""

if target_audio in text:
    text = text.replace(target_audio, rep_audio)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected HTML Custom Player")
else:
    print("HTML Audio not found")

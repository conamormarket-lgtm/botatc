import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = "        window.toggleSendMicButton = function() {"

rep = """        // CUSTOM AUDIO PLAYER LOGIC
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
            container.querySelector('.cap-progress').style.width = (percent * 100) + '%';
            container.querySelector('.cap-time').textContent = window.formatAudioTime(audio.currentTime);
        };

        window.toggleSendMicButton = function() {"""

if target in text:
    text = text.replace(target, rep)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected JS for Audio")
else:
    print("JS Target not found")

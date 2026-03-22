document.addEventListener('DOMContentLoaded', () => {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    const audioContext = AudioContextClass ? new AudioContextClass() : null;
    // Referencia al <audio> global del template base.
    const backgroundMusic = document.getElementById('background-music');
    // Contenedor visual de botones de audio.
    const musicControls = document.querySelector('.music-controls');
    // Botones de control de volumen en la esquina inferior.
    const volumeDownBtn = document.getElementById('music-volume-down');
    const volumeUpBtn = document.getElementById('music-volume-up');
    const muteToggleBtn = document.getElementById('music-mute-toggle');
    // Claves para persistir estado de música entre paginas (ej: login -> juegos).
    const MUSIC_STATE_KEYS = {
        shouldPlay: 'sudaplay_music_should_play',
        volume: 'sudaplay_music_volume',
        muted: 'sudaplay_music_muted',
        time: 'sudaplay_music_time',
        track: 'sudaplay_music_track',
    };
    // Evita intentar iniciar la pista de fondo en cada click.
    let backgroundMusicStarted = false;

    // Guarda estado actual para restaurarlo tras navegación.
    const persistMusicState = () => {
        if (!backgroundMusic) {
            return;
        }
        localStorage.setItem(MUSIC_STATE_KEYS.shouldPlay, backgroundMusic.paused ? '0' : '1');
        localStorage.setItem(MUSIC_STATE_KEYS.volume, String(backgroundMusic.volume));
        localStorage.setItem(MUSIC_STATE_KEYS.muted, backgroundMusic.muted ? '1' : '0');
        sessionStorage.setItem(MUSIC_STATE_KEYS.time, String(backgroundMusic.currentTime || 0));
    };

    // Restaura estado guardado (volumen/mute/tiempo) y trata de seguir reproduciendo.
    const restoreMusicState = () => {
        if (!backgroundMusic) {
            return;
        }

        const savedVolume = parseFloat(localStorage.getItem(MUSIC_STATE_KEYS.volume) || '');
        const savedMuted = localStorage.getItem(MUSIC_STATE_KEYS.muted);
        const savedTime = parseFloat(sessionStorage.getItem(MUSIC_STATE_KEYS.time) || '');
        const shouldPlay = localStorage.getItem(MUSIC_STATE_KEYS.shouldPlay) === '1';
        const savedTrack = localStorage.getItem(MUSIC_STATE_KEYS.track);

        if (savedTrack && backgroundMusic.getAttribute('src') !== savedTrack) {
            backgroundMusic.setAttribute('src', savedTrack);
            backgroundMusic.load();
        }

        if (!Number.isNaN(savedVolume)) {
            backgroundMusic.volume = Math.min(1, Math.max(0, savedVolume));
        } else {
            backgroundMusic.volume = 0.20;
        }

        if (savedMuted === '1' || savedMuted === '0') {
            backgroundMusic.muted = savedMuted === '1';
        }

        const applySavedTime = () => {
            if (!Number.isNaN(savedTime) && savedTime > 0 && Number.isFinite(backgroundMusic.duration)) {
                backgroundMusic.currentTime = Math.min(savedTime, Math.max(0, backgroundMusic.duration - 0.2));
            }
        };
        backgroundMusic.addEventListener('loadedmetadata', applySavedTime, { once: true });
        if (backgroundMusic.readyState >= 1) {
            applySavedTime();
        }
        // Intenta restaurar la reproduccion automaticamente.
        backgroundMusic.play().then(() => {
            backgroundMusicStarted = true;
        }).catch(() => { });
    };

    // Genera un sonido corto tipo click cada vez que el usuario toca o hace click.
    const playClickTone = () => {
        if (!audioContext) {
            return;
        }

        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        const filterNode = audioContext.createBiquadFilter();
        const now = audioContext.currentTime;

        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(1200, now);
        oscillator.frequency.exponentialRampToValueAtTime(600, now + 0.05);

        filterNode.type = 'highpass';
        filterNode.frequency.setValueAtTime(800, now);
        filterNode.Q.value = 2.2;

        gainNode.gain.setValueAtTime(0.0001, now);
        gainNode.gain.exponentialRampToValueAtTime(0.08, now + 0.004);
        gainNode.gain.exponentialRampToValueAtTime(0.0001, now + 0.07);

        oscillator.connect(filterNode);
        filterNode.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.start(now);
        oscillator.stop(now + 0.075);
    };

    // INTERACTIVE_TAGS: tags que deben producir click-tone (mejora rendimiento).
    const INTERACTIVE_TAGS = new Set(['A', 'BUTTON', 'INPUT', 'SELECT', 'LABEL', 'TEXTAREA']);

    // El navegador bloquea autoplay: se reanuda el audio al primer gesto
    // y se reproduce el click SOLO en elementos interactivos.
    const activateAudioFromGesture = (event) => {
        if (!audioContext) {
            return;
        }
        // Solo emitir tono si el pointerdown es sobre un elemento interactivo.
        const target = event.target;
        const isInteractive = target && (
            INTERACTIVE_TAGS.has(target.tagName) ||
            target.closest('a, button, [role="button"], [tabindex]')
        );

        audioContext.resume().then(() => {
            if (isInteractive) {
                playClickTone();
            }
        }).catch(() => { });

        // Inicia el MP3 de fondo.
        if (backgroundMusic && !backgroundMusicStarted) {
            if (!localStorage.getItem(MUSIC_STATE_KEYS.volume)) {
                backgroundMusic.volume = 0.24;
            }

            const savedTrack = localStorage.getItem(MUSIC_STATE_KEYS.track);
            if (savedTrack && backgroundMusic.getAttribute('src') !== savedTrack) {
                backgroundMusic.setAttribute('src', savedTrack);
                backgroundMusic.load();
            }

            backgroundMusic.play().then(() => {
                backgroundMusicStarted = true;
                persistMusicState();
            }).catch(() => { });
        }
    };

    document.addEventListener('pointerdown', activateAudioFromGesture, { passive: true });

    // Mantiene el texto/estado visual del botón de mute.
    const updateMuteButtonState = () => {
        if (!backgroundMusic) {
            return;
        }
        const isMuted = backgroundMusic.muted || backgroundMusic.volume === 0;

        if (muteToggleBtn) {
            muteToggleBtn.textContent = isMuted ? '\uD83D\uDD07' : '\uD83D\uDD0A';
            muteToggleBtn.classList.toggle('is-muted', isMuted);
        }

        // Actualizar también el icono del sidebar si existe
        const sidebarSoundIcon = document.querySelector('.secondary-nav-sound i');
        if (sidebarSoundIcon) {
            sidebarSoundIcon.className = isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up';
        }
    };

    // Controles: bajar/subir volumen y mutear.
    if (backgroundMusic) {
        const changeVolume = (delta) => {
            const nextVolume = Math.min(1, Math.max(0, backgroundMusic.volume + delta));
            backgroundMusic.volume = Number(nextVolume.toFixed(2));
            if (backgroundMusic.volume > 0 && backgroundMusic.muted) {
                backgroundMusic.muted = false;
            }
            updateMuteButtonState();
            persistMusicState();
        };

        if (volumeDownBtn) {
            volumeDownBtn.addEventListener('click', () => {
                changeVolume(-0.1);
            });
        }

        if (volumeUpBtn) {
            volumeUpBtn.addEventListener('click', () => {
                changeVolume(0.1);
            });
        }

        if (muteToggleBtn) {
            muteToggleBtn.addEventListener('click', () => {
                backgroundMusic.muted = !backgroundMusic.muted;
                updateMuteButtonState();
                persistMusicState();
            });
        }

        // Manejo del botón de toggle para expandir/contraer controles
        const musicControls = document.querySelector('.music-controls');
        const toggleExpandBtn = document.getElementById('music-toggle-expand');

        if (toggleExpandBtn && musicControls) {
            toggleExpandBtn.addEventListener('click', () => {
                musicControls.classList.toggle('expanded');
            });
        }

        restoreMusicState();
        updateMuteButtonState();
        window.addEventListener('pagehide', persistMusicState);
    }

    const closeButtons = document.querySelectorAll('.close');

});

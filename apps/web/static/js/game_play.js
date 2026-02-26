(function () {
    const stage = document.getElementById("play-stage");
    const frame = stage ? stage.querySelector(".play-frame") : null;
    const fullscreenBtn = document.getElementById("fullscreen-btn");
    const pauseOverlay = document.getElementById("play-pause-overlay");
    const resumeBtn = document.getElementById("play-resume-btn");
    let gameStarted = false;
    let wasFullscreen = false;
    if (!stage || !fullscreenBtn) return;

    function suppressModalDialogs(targetWindow) {
        if (!targetWindow) return;
        try {
            targetWindow.alert = function () { };
            targetWindow.confirm = function () { return false; };
            targetWindow.prompt = function () { return null; };
        } catch (err) {
            // Ignorar por politicas de origen cruzado.
        }
    }

    suppressModalDialogs(window);

    if (frame) {
        frame.addEventListener("load", () => {
            try {
                suppressModalDialogs(frame.contentWindow);
            } catch (err) {
                // Ignorar por politicas de origen cruzado.
            }
        });
    }

    function setPausedState(isPaused) {
        if (pauseOverlay) {
            pauseOverlay.classList.toggle("is-hidden", !isPaused);
        }
        if (frame) {
            frame.style.pointerEvents = isPaused ? "none" : "auto";

            // Intentar pausar ejecuciones en el iframe (audio, video, eventos)
            try {
                const win = frame.contentWindow;
                if (win) {
                    // Enviar señal de postMessage por si el juego tiene un receptor
                    win.postMessage({ type: isPaused ? 'sudaplay_pause' : 'sudaplay_resume' }, "*");

                    if (isPaused) {
                        // Simular pérdida de foco para que motores como Phaser/Unity se pausen
                        win.dispatchEvent(new Event('blur'));

                        // Pausar elementos multimedia si es mismo origen
                        const media = win.document.querySelectorAll("audio, video");
                        media.forEach(m => m.pause());
                    } else {
                        // Simular ganancia de foco
                        win.dispatchEvent(new Event('focus'));
                        frame.focus();
                    }
                }
            } catch (e) {
                // Ignorar errores de origen cruzado
            }
        }
    }

    function startGame() {
        if (!frame) return;
        if (!gameStarted) {
            const targetSrc = frame.dataset.src;
            if (!targetSrc) return;
            frame.src = targetSrc;
            gameStarted = true;
        }
        setPausedState(false);
        frame.focus();
    }

    if (resumeBtn) {
        resumeBtn.addEventListener("click", startGame);
    }

    function isFullscreenActive() {
        return document.fullscreenElement || document.webkitFullscreenElement;
    }

    function updateButtonLabel() {
        fullscreenBtn.textContent = isFullscreenActive()
            ? "Pantalla completa activada (ESC para salir)"
            : "Pantalla completa";
    }

    async function openFullscreen() {
        if (stage.requestFullscreen) {
            await stage.requestFullscreen();
            return;
        }
        if (stage.webkitRequestFullscreen) {
            stage.webkitRequestFullscreen();
        }
    }

    fullscreenBtn.addEventListener("click", async () => {
        if (isFullscreenActive()) {
            return;
        }
        try {
            await openFullscreen();
        } catch (err) {
            console.error("No se pudo cambiar a pantalla completa:", err);
        }
        updateButtonLabel();
        if (frame) {
            frame.focus();
        }
    });

    function handleFullscreenChange() {
        const active = isFullscreenActive();
        // Eliminamos la pausa automática al salir de pantalla completa (Escape)
        // para evitar que aparezca el icono de "Jugar".
        wasFullscreen = Boolean(active);
        updateButtonLabel();
        if (active && frame) {
            frame.focus();
        }
    }
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    document.addEventListener("webkitfullscreenchange", handleFullscreenChange);
    wasFullscreen = Boolean(isFullscreenActive());
    updateButtonLabel();

    // Evitar scroll cuando el juego está iniciado
    const blockScroll = (e) => {
        if (!gameStarted) return;

        const isTyping = ["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName);
        if (isTyping) return;

        const keys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " ", "Spacebar"];
        if (keys.includes(e.key)) {
            e.preventDefault();
        }
    };

    window.addEventListener("keydown", blockScroll, { passive: false });

    // Intentar bloquear scroll incluso si el foco está dentro del iframe (mismo origen)
    if (frame) {
        frame.addEventListener("load", () => {
            try {
                frame.contentWindow.addEventListener("keydown", blockScroll, { passive: false });
            } catch (e) {
                // Ignorar si es de origen cruzado
            }
        });
    }

    // Si el usuario hace clic en el área de juego, forzar foco al iframe
    if (stage) {
        stage.addEventListener("mousedown", () => {
            if (gameStarted && frame) {
                setTimeout(() => frame.focus(), 10);
            }
        });
    }
})();

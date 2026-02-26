// Funcionalidad para cerrar mensajes
document.addEventListener('DOMContentLoaded', function () {
    // Compatibilidad de AudioContext entre navegadores.
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

    // El navegador bloquea autoplay: se reanuda el audio al primer gesto
    // y se reproduce el click en cada pointerdown.
    const activateAudioFromGesture = () => {
        if (!audioContext) {
            return;
        }
        audioContext.resume().then(() => {
            playClickTone();
        }).catch(() => { });

        // Inicia el MP3 de fondo .
        if (backgroundMusic && !backgroundMusicStarted) {
            if (!localStorage.getItem(MUSIC_STATE_KEYS.volume)) {
                backgroundMusic.volume = 0.24;
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

    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            this.closest('.alert').style.display = 'none';
        });
    });

    // Auto-cerrar mensajes despues de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });

    // Funcionalidad para mostrar el footer
    const footer = document.querySelector('.footer');
    let displayTimeout;

    if (footer) {
        const showFooter = () => {
            footer.classList.add('show');
            clearTimeout(displayTimeout);
            displayTimeout = setTimeout(() => {
                footer.classList.remove('show');
            }, 2000); // Se oculta tras 2 segundos
        };

        // Mostrar al hacer scroll
        window.addEventListener('scroll', showFooter, { passive: true });
        document.body.addEventListener('scroll', showFooter, { passive: true });

        // Mostrar al tocar la pantalla (para mÃ³viles)
        window.addEventListener('touchstart', showFooter, { passive: true });
    }

    const profileDropdown = document.querySelector('.profile-dropdown');
    const profileToggle = document.querySelector('.profile-dropdown-toggle');


    if (profileDropdown && profileToggle) {
        const closeMenu = () => {
            profileDropdown.classList.remove('open');
            profileToggle.setAttribute('aria-expanded', 'false');
        };

        profileToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const isOpen = profileDropdown.classList.toggle('open');
            profileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        document.addEventListener('click', (event) => {
            if (!profileDropdown.contains(event.target)) {
                closeMenu();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeMenu();
            }
        });
    }

    const centeredNavLinks = Array.from(document.querySelectorAll('.nav-links-centered .nav-item'));
    if (centeredNavLinks.length > 0) {
        const normalizePath = (value) => {
            const path = (value || '/').replace(/\/+$/, '');
            return path === '' ? '/' : path;
        };

        const updateHeaderActiveLink = () => {
            const currentPath = normalizePath(window.location.pathname);
            const currentHash = (window.location.hash || '').toLowerCase();
            const isCatalogSection = currentHash === '#catalogo-juegos';

            document.body.classList.toggle('catalogo-focus', isCatalogSection);

            centeredNavLinks.forEach((link) => {
                const linkUrl = new URL(link.href, window.location.origin);
                const linkPath = normalizePath(linkUrl.pathname);
                const linkHash = (linkUrl.hash || '').toLowerCase();

                let isActive = false;
                if (linkHash) {
                    isActive = linkPath === currentPath && linkHash === currentHash;
                } else {
                    isActive = linkPath === currentPath && !currentHash;
                }

                link.classList.toggle('is-active', isActive);
            });

            if (!centeredNavLinks.some((link) => link.classList.contains('is-active'))) {
                const fallback = centeredNavLinks.find((link) => {
                    const linkUrl = new URL(link.href, window.location.origin);
                    return normalizePath(linkUrl.pathname) === currentPath && !linkUrl.hash;
                });
                if (fallback) {
                    fallback.classList.add('is-active');
                }
            }
        };

        updateHeaderActiveLink();
        window.addEventListener('hashchange', updateHeaderActiveLink);
    }

    const backLinks = Array.from(document.querySelectorAll('[data-back-link="true"]'));
    backLinks.forEach((link) => {
        link.addEventListener('click', (event) => {
            if (window.history.length > 1) {
                event.preventDefault();
                window.history.back();
            }
        });
    });

    const loginRequiredLinks = Array.from(document.querySelectorAll('[data-login-required="true"]'));
    const loginRequiredPanel = document.getElementById('login-required-panel');
    const closeLoginRequiredPanelBtn = document.getElementById('close-login-required-panel');
    const continueLoginRequiredPanelBtn = document.getElementById('continue-login-required-panel');

    if (loginRequiredLinks.length > 0 && loginRequiredPanel) {
        const buildLoginUrlWithNext = (targetUrl) => {
            const loginBase = loginRequiredPanel.dataset.loginBase || '/auth/login/';
            const loginUrl = new URL(loginBase, window.location.origin);
            const target = new URL(targetUrl, window.location.origin);
            const nextPath = `${target.pathname}${target.search}${target.hash}`;
            loginUrl.searchParams.set('next', nextPath);
            return loginUrl.toString();
        };

        const closeLoginRequiredPanel = () => {
            loginRequiredPanel.classList.remove('is-open');
            loginRequiredPanel.setAttribute('aria-hidden', 'true');
        };

        const openLoginRequiredPanel = (targetUrl) => {
            if (continueLoginRequiredPanelBtn && targetUrl) {
                continueLoginRequiredPanelBtn.href = buildLoginUrlWithNext(targetUrl);
            }
            loginRequiredPanel.classList.add('is-open');
            loginRequiredPanel.setAttribute('aria-hidden', 'false');
        };

        loginRequiredLinks.forEach((link) => {
            link.addEventListener('click', (event) => {
                event.preventDefault();
                openLoginRequiredPanel(link.href);
            });
        });

        if (closeLoginRequiredPanelBtn) {
            closeLoginRequiredPanelBtn.addEventListener('click', () => {
                closeLoginRequiredPanel();
            });
        }

        loginRequiredPanel.addEventListener('click', (event) => {
            if (event.target === loginRequiredPanel) {
                closeLoginRequiredPanel();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeLoginRequiredPanel();
            }
        });
    }

    // SIDEBAR TOGGLE & SOPORTE, solo para usuarios logueados (detectado por la existencia del dropdown de perfil)
    const navbarContainer = document.querySelector('.navbar-container');
    const navbarBrand = document.querySelector('.navbar-brand');
    
    // Verificamos si el usuario esta logueado buscando el dropdown de perfil
    const isUserLoggedIn = document.querySelector('.profile-dropdown');

    if (isUserLoggedIn) {
        let sidebar = document.querySelector('.secondary-nav');

        if (!sidebar) {
            sidebar = document.createElement('aside');
            sidebar.className = 'secondary-nav';
            sidebar.innerHTML = '<div class="secondary-nav-container"></div>';
            // Insertar al principio del body para que el z-index funcione bien
            document.body.insertBefore(sidebar, document.body.firstChild);
        }
        
        // Marca el body para ajustar margenes CSS
        document.body.classList.add('has-sidebar');

        if (navbarContainer && navbarBrand && sidebar) {
            if (!document.getElementById('sidebar-toggle')) {
                const toggleBtn = document.createElement('button');
                toggleBtn.id = 'sidebar-toggle';
                toggleBtn.className = 'sidebar-toggle';
                toggleBtn.innerHTML = '<i class="fas fa-bars"></i>'; // Icono hamburguesa
                toggleBtn.setAttribute('aria-label', 'Abrir/Cerrar Menú');
                navbarContainer.insertBefore(toggleBtn, navbarBrand);

                // Lógica de click
                toggleBtn.addEventListener('click', () => {
                    const isNowOpen = document.body.classList.toggle('sidebar-open');
                    localStorage.setItem('sudaplay_sidebar_state', isNowOpen ? 'open' : 'closed');
                });

                // Restaurar estado guardado
                if (localStorage.getItem('sudaplay_sidebar_state') === 'open') {
                    document.body.classList.add('sidebar-open');
                }
            }

            //   Icono de Sonido y Soporte al Sidebar
            const sidebarContainer = sidebar.querySelector('.secondary-nav-container');
            
            if (sidebarContainer && !sidebarContainer.querySelector('.secondary-nav-sound')) {
                const soundLink = document.createElement('a');
                soundLink.href = '#';
                soundLink.className = 'secondary-nav-item secondary-nav-sound mt-auto'; // Empuja al fondo
                const isMuted = backgroundMusic ? backgroundMusic.muted : false;
                soundLink.innerHTML = isMuted ? '<i class="fas fa-volume-mute"></i><span>Sonido</span>' : '<i class="fas fa-volume-up"></i><span>Sonido</span>';
                
                soundLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (backgroundMusic) {
                        backgroundMusic.muted = !backgroundMusic.muted;
                        updateMuteButtonState();
                        persistMusicState();
                    }
                });
                sidebarContainer.appendChild(soundLink);
            }

            //  Botón Bajar Volumen
            if (sidebarContainer && !sidebarContainer.querySelector('.secondary-nav-vol-down')) {
                const volDownLink = document.createElement('a');
                volDownLink.href = '#';
                volDownLink.className = 'secondary-nav-item secondary-nav-vol-down';
                volDownLink.innerHTML = '<i class="fas fa-minus"></i>';
                
                volDownLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (backgroundMusic) {
                        const nextVolume = Math.min(1, Math.max(0, backgroundMusic.volume - 0.1));
                        backgroundMusic.volume = Number(nextVolume.toFixed(2));
                        if (backgroundMusic.volume > 0 && backgroundMusic.muted) {
                            backgroundMusic.muted = false;
                        }
                        updateMuteButtonState();
                        persistMusicState();
                    }
                });
                sidebarContainer.appendChild(volDownLink);
            }

            // Botón Subir Volumen
            if (sidebarContainer && !sidebarContainer.querySelector('.secondary-nav-vol-up')) {
                const volUpLink = document.createElement('a');
                volUpLink.href = '#';
                volUpLink.className = 'secondary-nav-item secondary-nav-vol-up';
                volUpLink.innerHTML = '<i class="fas fa-plus"></i>';
                
                volUpLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (backgroundMusic) {
                        const nextVolume = Math.min(1, Math.max(0, backgroundMusic.volume + 0.1));
                        backgroundMusic.volume = Number(nextVolume.toFixed(2));
                        if (backgroundMusic.volume > 0 && backgroundMusic.muted) {
                            backgroundMusic.muted = false;
                        }
                        updateMuteButtonState();
                        persistMusicState();
                    }
                });
                sidebarContainer.appendChild(volUpLink);
            }

            // Botón de Soporte
            if (sidebarContainer && !sidebarContainer.querySelector('.secondary-nav-support')) {
                const supportLink = document.createElement('a');
                supportLink.href = '#'; // Puedes cambiar esto por la URL real de soporte
                supportLink.className = 'secondary-nav-item secondary-nav-support'; // Se apila debajo del sonido
                supportLink.innerHTML = '<i class="fas fa-headset"></i><span>Soporte</span>';
                sidebarContainer.appendChild(supportLink);
            }

            //  Botón Cerrar Sesión
            if (sidebarContainer && !sidebarContainer.querySelector('.secondary-nav-logout')) {
                const logoutLink = document.createElement('a');
                logoutLink.href = '/auth/logout/';
                logoutLink.className = 'secondary-nav-item secondary-nav-logout';
                logoutLink.innerHTML = '<i class="fas fa-sign-out-alt"></i><span>Cerrar Sesión</span>';
                sidebarContainer.appendChild(logoutLink);
            }
        }
    }

});

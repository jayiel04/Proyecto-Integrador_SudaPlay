document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.secondary-nav');
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

        // Mostrar al tocar la pantalla 
        window.addEventListener('touchstart', showFooter, { passive: true });
    }

    const normalizePath = (value) => {
        const path = (value || '/').replace(/\/+$/, '');
        return path === '' ? '/' : path;
    };

    // también marcamos el icono correspondiente en el sidebar
    const updateSidebarActive = () => {
        const currentPath = normalizePath(window.location.pathname);
        const currentHash = (window.location.hash || '').toLowerCase();
        if (!sidebar) return;
        const container = sidebar.querySelector('.secondary-nav-container');
        if (!container) return;
        const mappings = [
            { selector: '.secondary-nav-games', path: normalizePath('/'), hash: '#catalogo-juegos' },
            { selector: '.secondary-nav-upload', path: normalizePath('/juegos/subir/') },
            { selector: '.secondary-nav-normas', path: normalizePath('/juegos/normas/') },
            { selector: '.secondary-nav-about', path: normalizePath('/juegos/acerca-de/') },
        ];
        mappings.forEach(item => {
            const el = container.querySelector(item.selector);
            if (!el) return;
            let active = false;
            if (item.hash) {
                active = currentPath === item.path && currentHash === item.hash;
            } else {
                active = currentPath === item.path;
            }
            el.classList.toggle('is-active', active);
        });
    };

    const centeredNavLinks = Array.from(document.querySelectorAll('.nav-links-centered .nav-item'));
    if (centeredNavLinks.length > 0) {
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

    // Activar sidebar links active state
    window.addEventListener('hashchange', updateSidebarActive);
    updateSidebarActive();

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

    let openLoginRequiredPanel = () => { };
    if (loginRequiredPanel) {
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

        openLoginRequiredPanel = (targetUrl) => {
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

    // SIDEBAR TOGGLE & SOPORTE
    // El sidebar y el botón toggle ahora están en el HTML del template (base.html).
    // Este bloque solo conecta comportamientos (click, localStorage, sonido).
    const isAuthPage = document.body.classList.contains('body-auth-page');

    if (!isAuthPage) {
        // has-sidebar ya viene en el HTML del servidor (base.html) — no añadir aqui para evitar CLS.

        // Restaurar estado del sidebar y conectar toggle
        const toggleBtn = document.getElementById('sidebar-toggle');
        if (toggleBtn) {
            if (localStorage.getItem('sudaplay_sidebar_state') === 'open') {
                document.body.classList.add('sidebar-open');
            }
            toggleBtn.addEventListener('click', () => {
                const isNowOpen = document.body.classList.toggle('sidebar-open');
                localStorage.setItem('sudaplay_sidebar_state', isNowOpen ? 'open' : 'closed');
            });
        }

        // Marcar active state en el sidebar
        updateSidebarActive();
    }
});

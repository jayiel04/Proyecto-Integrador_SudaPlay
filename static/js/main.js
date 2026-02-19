// Funcionalidad para cerrar mensajes
document.addEventListener('DOMContentLoaded', function () {
    const closeButtons = document.querySelectorAll('.close');

    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            this.closest('.alert').style.display = 'none';
        });
    });

    // Auto-cerrar mensajes después de 5 segundos
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

        // Mostrar al tocar la pantalla (para móviles)
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

    const gameCards = Array.from(document.querySelectorAll('.game-item[data-detail-url]'));
    if (gameCards.length > 0) {
        const goToCardDetail = (card) => {
            const url = card.dataset.detailUrl;
            if (url) {
                window.location.href = url;
            }
        };

        gameCards.forEach((card) => {
            card.addEventListener('click', (event) => {
                if (event.target.closest('a, button, input, textarea, select, label')) {
                    return;
                }
                goToCardDetail(card);
            });

            card.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    goToCardDetail(card);
                }
            });
        });
    }

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
            closeLoginRequiredPanelBtn.addEventListener('click', closeLoginRequiredPanel);
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
});

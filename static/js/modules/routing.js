document.addEventListener('DOMContentLoaded', () => {
    // Espera la carga de estilos antes de permitir navegacion/recarga.
    const styleLinks = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
    let stylesReadyPromise = null;
    let navigationLocked = false;
    let navigationUnlockTimer = null;

    const lockNavigation = (durationMs) => {
        navigationLocked = true;
        if (navigationUnlockTimer) {
            clearTimeout(navigationUnlockTimer);
        }
        navigationUnlockTimer = setTimeout(() => {
            navigationLocked = false;
            navigationUnlockTimer = null;
        }, durationMs);
    };

    const isStylesheetReady = (linkEl) => {
        if (linkEl.dataset.stylesheetReady === '1') {
            return true;
        }
        if (!linkEl.sheet) {
            return false;
        }
        try {
            // Si podemos leer cssRules, la hoja ya esta disponible.
            void linkEl.sheet.cssRules;
        } catch (error) {
            // SecurityError en hojas cross-origin: contarla como lista si existe sheet.
            if (error && error.name === 'SecurityError') {
                return true;
            }
        }
        return true;
    };

    const waitForStylesReady = () => {
        if (stylesReadyPromise) {
            return stylesReadyPromise;
        }
        // Verificar si todos los estilos ya están listos de forma síncrona
        const allReady = styleLinks.every(isStylesheetReady);
        if (allReady) {
            styleLinks.forEach(l => { l.dataset.stylesheetReady = '1'; });
            stylesReadyPromise = Promise.resolve();
            return stylesReadyPromise;
        }
        stylesReadyPromise = Promise.all(
            styleLinks.map((linkEl) => new Promise((resolve) => {
                if (isStylesheetReady(linkEl)) {
                    linkEl.dataset.stylesheetReady = '1';
                    resolve();
                    return;
                }

                const done = () => {
                    linkEl.dataset.stylesheetReady = '1';
                    resolve();
                };

                linkEl.addEventListener('load', done, { once: true });
                linkEl.addEventListener('error', done, { once: true });
                // Reducido de 2500ms a 1000ms para no bloquear demasiado.
                setTimeout(done, 1000);
            }))
        );
        return stylesReadyPromise;
    };

    waitForStylesReady().finally(() => {
        document.documentElement.classList.add('is-ready');
    });

    const runAfterStyles = (callback) => {
        if (navigationLocked) {
            return;
        }

        // Si los estilos ya están listos, navegar inmediatamente sin esperar la Promise.
        if (styleLinks.every(l => l.dataset.stylesheetReady === '1')) {
            // Lock corto para evitar dobles taps sin penalizar fluidez.
            lockNavigation(450);
            callback();
            return;
        }

        // Lock más largo solo cuando realmente hay espera de estilos.
        lockNavigation(1200);
        waitForStylesReady().finally(() => {
            callback();
        });
    };

    waitForStylesReady();
    window.addEventListener('pageshow', () => {
        // Al volver con historial (BFCache), desbloquea la navegacion.
        navigationLocked = false;
        if (navigationUnlockTimer) {
            clearTimeout(navigationUnlockTimer);
            navigationUnlockTimer = null;
        }
    });

    document.addEventListener('click', (event) => {
        if (event.defaultPrevented || event.button !== 0) {
            return;
        }
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
            return;
        }

        const link = event.target.closest('a[href]');
        if (!link) {
            return;
        }

        // EXCLUSIONES: Evitamos interceptar links con comportamientos especiales.
        if (
            link.dataset.noStyleWait === 'true' ||
            link.dataset.loginRequired === 'true' ||
            link.classList.contains('profile-chat-toggle') ||
            link.classList.contains('notification-toggle')
        ) {
            return;
        }

        if (link.target && link.target !== '_self') {
            return;
        }
        if (link.hasAttribute('download')) {
            return;
        }

        const targetUrl = new URL(link.href, window.location.href);
        if (targetUrl.origin !== window.location.origin) {
            return;
        }

        // En anchors de la misma pagina o links vacios no bloqueamos la navegacion.
        const sameDoc = targetUrl.pathname === window.location.pathname
            && targetUrl.search === window.location.search;
        if (sameDoc && (targetUrl.hash || targetUrl.href === window.location.href)) {
            return;
        }

        event.preventDefault();
        runAfterStyles(() => {
            window.location.assign(targetUrl.href);
        });
    }, true);

    document.addEventListener('submit', (event) => {
        if (event.defaultPrevented) {
            return;
        }
        const form = event.target;
        if (!(form instanceof HTMLFormElement)) {
            return;
        }
        if (form.dataset.noStyleWait === 'true') {
            return;
        }
        if (form.target && form.target !== '_self') {
            return;
        }

        event.preventDefault();
        runAfterStyles(() => {
            form.submit();
        });
    }, true);

    window.addEventListener('keydown', (event) => {
        if (event.defaultPrevented) {
            return;
        }
        const key = (event.key || '').toLowerCase();
        const isReloadShortcut = key === 'f5' || ((event.ctrlKey || event.metaKey) && key === 'r');
        if (!isReloadShortcut) {
            return;
        }

        event.preventDefault();
        runAfterStyles(() => {
            window.location.reload();
        });
    }, true);

    // Compatibilidad de AudioContext entre navegadores.

});

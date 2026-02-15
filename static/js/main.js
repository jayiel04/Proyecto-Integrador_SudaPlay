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
});

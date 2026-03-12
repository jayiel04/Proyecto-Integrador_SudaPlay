import sys

filepath = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\static\js\main.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        document.addEventListener('click', (event) => {
            if (!notificationWidget.contains(event.target)) {
                closeNotifications();
            }
        });
    }"""

normalized_content = content.replace('\r\n', '\n')

replacement = """        document.addEventListener('click', (event) => {
            if (!notificationWidget.contains(event.target)) {
                closeNotifications();
            }
        });

        // Actualizar notificaciones al cambiar de página (carga inicial) y cada 5 minutos
        loadNotifications();
        setInterval(loadNotifications, 300000); // 5 * 60 * 1000 = 300000 ms
    }"""

if target in normalized_content:
    new_content = normalized_content.replace(target, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('File updated successfully.')
else:
    print('Target not found.')

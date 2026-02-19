# Mi Proyecto Django - Documentación

## 📋 Descripción General

Este es un proyecto Django escalable y profesional con:
- Sistema de autenticación robusto
- Estructura organizada por aplicaciones
- Mejores prácticas de seguridad
- Class-Based Views
- Templates centralizados
- Gestión de archivos estáticos

---

## 🗂️ Estructura del Proyecto

```
Proyecto Integrador/
├── mi_proyecto/              # Configuración principal
│   ├── settings.py          # Variables de entorno y configuración
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # Servidor WSGI
│   └── asgi.py              # Servidor ASGI
├── login/                    # App de autenticación
│   ├── models.py            # Modelos (UserProfile)
│   ├── views.py             # Vistas de login
│   ├── urls.py              # URLs de login
│   ├── admin.py             # Admin personalizado
│   ├── migrations/          # Migraciones de base de datos
│   ├── templates/login/     # Templates de login
│   └── static/css/          # Estilos
├── web/                      # App principal
│   ├── models.py            # Modelos
│   ├── views.py             # Vistas
│   ├── urls.py              # URLs
│   └── admin.py             # Admin
├── templates/               # Templates centralizados
│   ├── base.html            # Template base
│   ├── home.html            # Inicio
│   └── login/
│       └── login.html       # Login
├── static/                  # Archivos estáticos
│   ├── css/
│   │   └── styles.css       # Estilos principales
│   ├── js/
│   │   └── main.js          # Scripts principales
│   └── images/              # Imágenes
├── media/                   # Archivos subidos
├── manage.py                # Comando principal de Django
├── db.sqlite3               # Base de datos
├── .env.example             # Ejemplo de variables de entorno
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Este archivo
```

---

## 🚀 Instalación y Configuración

### 1. Crear entorno virtual
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus valores
```

### 4. Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario
```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor
```bash
python manage.py runserver
```

Acceder a:
- App: http://localhost:8000/
- Admin: http://localhost:8000/admin/

---

## 📱 Aplicaciones

### **login** - Autenticación de Usuarios
- Modelo `UserProfile` extendido del User de Django
- Vista `LoginView` basada en clases
- Manejo de sesiones
- Admin personalizado

**Rutas:**
- `/auth/login/` - Iniciar sesión
- `/auth/logout/` - Cerrar sesión

### **web** - Aplicación Principal
- Vista `HomeView` protegida
- Dashboard de usuario
- Template base reutilizable

**Rutas:**
- `/` - Página de inicio

---

## 🔒 Seguridad

### Implementado:
- ✅ Variables de entorno para secrets
- ✅ CSRF Protection en formularios
- ✅ Session security
- ✅ Password validation
- ✅ Login required decorators
- ✅ SQL Injection prevention (ORM)
- ✅ XSS protection (templates)

### Para Producción:
- Cambiar `DEBUG = False`
- Usar `requirements-prod.txt`
- Configurar `ALLOWED_HOSTS`
- Usar base de datos PostgreSQL
- Habilitar SSL/HTTPS
- Usar secrets manager

---

## 🎨 Personalización

### Agregar Nueva Aplicación
```bash
python manage.py startapp nombre_app
```

Luego:
1. Crear `urls.py` en la app
2. Agregar URLs al proyecto en `mi_proyecto/urls.py`
3. Registrar en `INSTALLED_APPS`
4. Crear templates en `templates/nombre_app/`

### Agregar New Template
Crear en `templates/` y extender de `base.html`:
```html
{% extends "base.html" %}
{% block title %}Título{% endblock %}
{% block content %}
  <!-- Contenido aquí -->
{% endblock %}
```

### Agregar Estilos
Editar `static/css/styles.css` y usar variables CSS:
```css
color: var(--primary-color);
background: var(--light-gray);
```

---

## 🧪 Testing

```bash
python manage.py test
python manage.py test login
python manage.py test --verbosity=2
```

---

## 📊 Base de Datos

### Modelos Disponibles:
- `User` (Django Auth)
- `UserProfile` (Personalizado)

### Migraciones
```bash
python manage.py makemigrations          # Crear migraciones
python manage.py showmigrations          # Ver migraciones
python manage.py migrate                 # Aplicar migraciones
python manage.py migrate login zero      # Revertir a cero
```

---

## 🐛 Debugging

Usar Django Debug Toolbar (en desarrollo):
```bash
pip install django-debug-toolbar
# Agregar a INSTALLED_APPS y MIDDLEWARE
```

Ver logs:
```bash
tail -f logs/django.log
```

---

## 📦 Dependencias

Ver `requirements.txt`:
- Django 6.0.2+
- python-decouple
- Pillow (para imágenes)
- python-dotenv

---

## 🔄 Workflow Recomendado

1. **Desarrollo local**: `DEBUG=True` con SQLite
2. **Testing**: Usar fixtures y datos de prueba
3. **Deployment**: 
   - Usar PostgreSQL
   - Recolectar estáticos: `python manage.py collectstatic`
   - Usar Gunicorn: `gunicorn mi_proyecto.wsgi`
   - Configurar Nginx/Apache

---

## 📝 Buenas Prácticas Implementadas

✅ Separación de URLs por aplicación  
✅ Class-Based Views  
✅ Templates centralizados  
✅ Modelos bien estructurados  
✅ Admin personalizado  
✅ Variables de entorno  
✅ Decoradores de seguridad  
✅ Manejo de mensajes  
✅ Responsive design  
✅ Código documentado  

---

## 🎓 Mejoras Futuras

- [ ] Sistema de registro de usuarios
- [ ] Reset de contraseña por email
- [ ] Autenticación con redes sociales
- [ ] Two-factor authentication
- [ ] API REST con DRF
- [ ] Caché con Redis
- [ ] Task queue con Celery
- [ ] Tests con pytest
- [ ] Docker

---

## 📞 Soporte

Para preguntas o problemas, revisar:
- [Documentación Django](https://docs.djangoproject.com/)
- [Django Security](https://docs.djangoproject.com/en/6.0/topics/security/)

---

**Última actualización:** 10 de Febrero de 2026

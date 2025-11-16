# Sistema de Gestión de Empleados

Sistema web profesional para gestión de asistencia, control horario y administración de personal.

## Características

### Para Administradores 👑
- ✅ Dashboard completo con estadísticas en tiempo real
- ✅ Gestión de usuarios (crear, modificar, bloquear, eliminar)
- ✅ Cambiar contraseñas de cualquier usuario
- ✅ Editar y borrar registros de asistencia
- ✅ Exportar datos a CSV con cálculo de horas extras
- ✅ Ver todos los registros de todos los empleados
- ✅ Desbloquear/bloquear cuentas de usuarios

### Para Usuarios 📋
- ✅ Marcar inicio de jornada
- ✅ Marcar salida de jornada
- ✅ Ver su propio historial de registros
- ✅ Cambiar su propia contraseña
- ✅ Cálculo automático de horas trabajadas y horas extras

### Características Técnicas 🔧
- 🎨 Diseño moderno con animaciones y gradientes elegantes
- 🔒 Sistema de roles (Admin/Usuario)
- 📊 Gráficos y estadísticas en tiempo real
- 💾 Almacenamiento en JSON (migrable a SQL)
- 🌐 Preparado para deployment remoto con HTTPS
- 📱 Responsive design (funciona en móviles y tablets)
- ⏰ No reemplaza registros anteriores (mantiene histórico completo)

## Instalación Local

### Requisitos
- Python 3.8+
- pip

### Pasos

1. **Clonar/Descargar el proyecto**
   ```bash
   cd app_web_empleados
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

4. **Abrir en navegador**
   ```
   http://127.0.0.1:5000
   ```

### Credenciales Iniciales

**Administrador:**
- Usuario: `LuisMolina`
- Contraseña: `Mathiasmc`

⚠️ **IMPORTANTE:** Cambia esta contraseña después del primer inicio de sesión.

## Deployment Remoto 🌐

Para acceder desde cualquier dispositivo y red (sin necesidad de tener tu equipo encendido):

### Opción Recomendada: Render.com

1. **Sube tu código a GitHub**
2. **Crea cuenta en [Render.com](https://render.com)**
3. **Crea un nuevo Web Service**
4. **Conecta tu repositorio de GitHub**
5. **Configura:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Agrega variable de entorno `SECRET_KEY` (genera una clave aleatoria)

6. **Deploy automático** ✅

Tu app estará disponible en: `https://tu-app.onrender.com`

**Características:**
- ✅ Gratis
- ✅ HTTPS automático (seguro)
- ✅ Activo 24/7
- ✅ No requiere tu equipo encendido

📖 **Guía completa de deployment:** Ver [DEPLOYMENT.md](DEPLOYMENT.md)

## Estructura del Proyecto

```
app_web_empleados/
├── app.py                      # Aplicación Flask principal
├── requirements.txt            # Dependencias Python
├── Procfile                    # Configuración para deployment
├── empleados_data.json         # Base de datos (JSON)
├── Templates/                  # Plantillas HTML
│   ├── base.html
│   ├── login.html             # Página de inicio de sesión
│   ├── register.html          # Página de registro
│   ├── dashboard.html         # Dashboard principal
│   ├── admin_usuarios.html    # Gestión de usuarios (admin)
│   ├── admin_cambiar_clave.html
│   └── ...
├── static/                     # Archivos estáticos (CSS, JS, imágenes)
├── AGENTS.md                   # Guía para desarrolladores
├── DEPLOYMENT.md               # Guía de deployment
└── README.md                   # Este archivo
```

## Seguridad 🔒

- 🔐 Sesiones seguras con Flask
- 🔑 Sistema de roles y permisos
- 🚫 Usuarios bloqueados no pueden acceder
- 🔒 HTTPS en producción (Render, Railway, Heroku)
- 🛡️ Validación de permisos en todas las rutas administrativas

### Mejoras de Seguridad Recomendadas

Para producción, considera:
1. Hashear contraseñas (usar `werkzeug.security`)
2. Migrar a base de datos SQL (PostgreSQL/MySQL)
3. Implementar rate limiting
4. Agregar autenticación de 2 factores
5. Logs de auditoría

## Uso

### Como Administrador

1. Inicia sesión con credenciales de admin
2. Accede al **Dashboard** para ver estadísticas
3. Ve a **Gestión de Usuarios** para administrar personal
4. Desde ahí puedes:
   - Cambiar contraseñas
   - Bloquear/desbloquear usuarios
   - Editar registros de asistencia
   - Borrar registros
   - Eliminar usuarios
5. Exporta datos a CSV cuando lo necesites

### Como Usuario Normal

1. Inicia sesión con tus credenciales
2. En el Dashboard verás tus registros
3. Marca tu **Inicio** al comenzar tu jornada
4. Marca tu **Salida** al terminar
5. El sistema calcula automáticamente:
   - Horas trabajadas
   - Horas extras (según el día de la semana)

## Cálculo de Horas Extras

- **Lunes a Viernes:** Más de 8 horas = extras al 125%
- **Sábado:** Extras al 175%
- **Domingo:** Extras al 200%

Basado en salario mínimo Colombia 2025: $1,384,308

## Soporte y Contacto

Para preguntas o soporte:
- Email: lemolina0323@gmail.com
- Repositorio: https://github.com/TheFaysal24/app_web_empleados

## Licencia

Este proyecto es privado y de uso interno.

---

**Desarrollado con ❤️ usando Flask y Python**

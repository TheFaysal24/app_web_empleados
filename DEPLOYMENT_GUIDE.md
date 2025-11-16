# 🚀 Guía de Despliegue en Render

## Pasos para Desplegar en Render

### 1. Preparación del Repositorio
✅ El código ya está en GitHub: https://github.com/TheFaysal24/app_web_empleados

### 2. Crear Cuenta en Render
1. Ve a [render.com](https://render.com)
2. Crea una cuenta o inicia sesión con GitHub

### 3. Conectar el Repositorio
1. En el dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu cuenta de GitHub si no lo has hecho
4. Busca y selecciona el repositorio: `TheFaysal24/app_web_empleados`
5. Haz clic en **"Connect"**

### 4. Configurar el Servicio

Usa la siguiente configuración:

- **Name**: `app-web-empleados` (o el nombre que prefieras)
- **Region**: Selecciona la región más cercana
- **Branch**: `main`
- **Root Directory**: (déjalo vacío)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 5. Variables de Entorno

En la sección "Environment Variables", agrega:

- `SECRET_KEY`: Genera una clave secreta segura
- `PYTHON_VERSION`: `3.11.0`

### 6. Plan

- Selecciona el plan **Free** para empezar
- O selecciona un plan de pago para mejor rendimiento

### 7. Desplegar

1. Haz clic en **"Create Web Service"**
2. Render comenzará a construir y desplegar tu aplicación
3. El proceso toma aproximadamente 2-5 minutos

### 8. Acceder a la Aplicación

Una vez desplegado, Render te proporcionará una URL como:
```
https://app-web-empleados.onrender.com
```

O la URL personalizada que hayas configurado.

## 📋 Credenciales por Defecto

- **Usuario**: `admin`
- **Contraseña**: `1234`

## 🔄 Actualizaciones Automáticas

Render redesplegará automáticamente tu aplicación cada vez que hagas push a la rama `main` en GitHub.

## 🛠 Características Implementadas

✅ Sistema de turnos rotativos desde Nov 3, 2025
✅ Historial completo con trazabilidad
✅ Asignación automática por cédula
✅ Cargos de telecomunicaciones
✅ Notificaciones por Email y WhatsApp
✅ Flash messages de 1 segundo
✅ Dashboard interactivo

## 📞 Soporte

Para problemas o preguntas, revisa los logs en Render o contacta al administrador del sistema.

## 🔐 Seguridad

- Cambia las credenciales de administrador después del primer acceso
- Usa HTTPS (Render lo proporciona automáticamente)
- Configura backups regulares desde el panel de administración

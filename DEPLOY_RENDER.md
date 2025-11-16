# 🚀 Guía Completa de Despliegue en Render

## ✅ Preparación Completa

El repositorio ya está listo en: **https://github.com/TheFaysal24/app_web_empleados**

## 📋 Pasos para Desplegar en Render

### 1. Crear Cuenta en Render
1. Ve a **https://render.com**
2. Haz clic en "Get Started for Free"
3. Conéctate con tu cuenta de GitHub

### 2. Crear Nuevo Web Service
1. En el dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu cuenta de GitHub si aún no lo has hecho
4. Busca el repositorio: **TheFaysal24/app_web_empleados**
5. Haz clic en **"Connect"**

### 3. Configuración del Servicio

Usa exactamente esta configuración:

```
Name: app-web-empleados
Region: Oregon (US West) o la más cercana
Branch: main
Root Directory: (dejar vacío)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

### 4. Variables de Entorno

En la sección "Environment", agrega:

```
SECRET_KEY = cualquier_cadena_aleatoria_segura_aqui
PYTHON_VERSION = 3.11.0
```

### 5. Plan y Despliegue

1. Selecciona el plan **Free** (suficiente para empezar)
2. Haz clic en **"Create Web Service"**
3. Espera 3-5 minutos mientras Render construye y despliega

### 6. URL de Acceso

Render te dará una URL como:
```
https://app-web-empleados.onrender.com
```

## 🔐 Credenciales Iniciales

### Administrador
- Usuario: `admin`
- Contraseña: `1234`

### Gestores Operativos
- `natalia.arevalo` - Contraseña: `1234`
- `lesly.guzman` - Contraseña: `1234`
- `paola.garcia` - Contraseña: `1234`
- `dayana.gonzalez` - Contraseña: `1234`

**⚠️ IMPORTANTE:** Cambia estas contraseñas después del primer acceso.

## 🔄 Actualizaciones Automáticas

Cada vez que hagas `git push` a la rama `main`, Render redesplegará automáticamente la aplicación.

## 🛠 Solución de Problemas

### Si falla el despliegue:

1. **Revisa los logs** en Render (pestaña "Logs")
2. **Verifica** que `requirements.txt` tenga:
   ```
   Flask==2.3.3
   gunicorn==21.2.0
   Werkzeug==2.3.7
   ```
3. **Asegúrate** de que el puerto sea dinámico: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Errores comunes:

- **"Template not found"**: Ya está resuelto con `template_folder='Templates'`
- **"Module not found"**: Verifica que `requirements.txt` esté completo
- **"Port already in use"**: Render maneja esto automáticamente

## 📊 Características Implementadas

✅ Sistema de turnos rotativos automático por cédula
✅ Historial completo desde Nov 3, 2025
✅ Panel de asignación manual para admin
✅ Control total de usuarios, contraseñas, turnos
✅ Edición de registros de asistencia
✅ Eliminación de turnos
✅ Resumen semanal por gestor
✅ Notificaciones por Email/WhatsApp
✅ Backups automáticos
✅ Exportación a CSV

## 🌐 Alternativa: Desplegar en Heroku

Si prefieres Heroku:

```bash
# Instalar Heroku CLI
# Luego ejecutar:
heroku login
heroku create app-web-empleados
git push heroku main
heroku open
```

## 📞 Soporte

Si necesitas ayuda:
- Revisa los logs en Render
- Verifica la documentación: https://render.com/docs
- GitHub Issues: https://github.com/TheFaysal24/app_web_empleados/issues

---

**¡Tu aplicación está lista para producción!** 🎉

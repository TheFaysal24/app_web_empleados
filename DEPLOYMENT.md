# Guía de Deployment - Sistema de Empleados

## Opciones de Deployment Remoto Seguro

### Opción 1: Render.com (RECOMENDADO - Gratis y Fácil)

Render.com ofrece hosting gratuito con SSL automático (HTTPS) y está activo 24/7.

#### Pasos:

1. **Crear cuenta en Render.com**
   - Ve a https://render.com
   - Regístrate con tu cuenta de GitHub/GitLab

2. **Preparar el proyecto**
   - Ya está configurado con `requirements.txt` y `Procfile.txt`
   - Renombrar `Procfile.txt` a `Procfile` (sin extensión)

3. **Conectar repositorio**
   - Sube tu código a GitHub (si no lo has hecho)
   - En Render, crea un nuevo "Web Service"
   - Conecta tu repositorio de GitHub

4. **Configurar el servicio**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
   - Agregar variable de entorno:
     - `SECRET_KEY`: [genera una clave aleatoria segura]

5. **Deploy**
   - Render automáticamente construirá y desplegará tu app
   - Obtendrás una URL tipo: `https://tu-app.onrender.com`
   - SSL/HTTPS automático ✅
   - Activo 24/7 ✅

---

### Opción 2: Railway.app (Fácil, con plan gratuito limitado)

1. **Crear cuenta en Railway.app**
   - https://railway.app
   - Registrarse con GitHub

2. **Deploy desde GitHub**
   - Nuevo Proyecto → Deploy from GitHub
   - Seleccionar tu repositorio
   - Railway detecta automáticamente Flask

3. **Variables de entorno**
   - Agregar `SECRET_KEY` en las variables de entorno

4. **Listo**
   - Railway te da un dominio: `https://tu-app.up.railway.app`
   - SSL automático ✅

---

### Opción 3: PythonAnywhere (Gratis, estable)

1. **Crear cuenta gratuita**
   - https://www.pythonanywhere.com
   - Plan gratuito incluye 1 web app

2. **Subir código**
   - Usar Git o cargar archivos manualmente
   - Desde consola Bash: `git clone [tu-repo]`

3. **Configurar Web App**
   - Web tab → Add a new web app
   - Seleccionar Flask
   - Apuntar a tu `app.py`

4. **HTTPS**
   - Plan gratuito: solo HTTP (http://tuusuario.pythonanywhere.com)
   - Plan pago: HTTPS disponible

---

### Opción 4: Heroku (Requiere tarjeta, sin cargo gratuito permanente)

1. **Crear cuenta en Heroku**
   - https://heroku.com
   - Requiere tarjeta de crédito (sin cargo inicial)

2. **Instalar Heroku CLI**
   - https://devcenter.heroku.com/articles/heroku-cli

3. **Deploy**
   ```bash
   heroku login
   heroku create nombre-de-tu-app
   git push heroku main
   ```

4. **Configurar variables**
   ```bash
   heroku config:set SECRET_KEY=tu-clave-secreta-segura
   ```

5. **Tu app estará en:**
   - `https://nombre-de-tu-app.herokuapp.com`
   - SSL automático ✅

---

## Seguridad Importante

### 1. Cambiar SECRET_KEY en producción

En `app.py`, línea 9, cambiar:
```python
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_para_sesiones')
```

Luego configurar en tu servicio de hosting la variable de entorno `SECRET_KEY` con una clave aleatoria larga (mínimo 32 caracteres).

Generar una clave segura en Python:
```python
import secrets
print(secrets.token_hex(32))
```

### 2. Usar HTTPS

- ✅ Render, Railway, Heroku: HTTPS automático
- ⚠️ PythonAnywhere gratuito: solo HTTP (considera plan pago para HTTPS)

### 3. Cambiar contraseña del admin

Después del primer deployment, cambia la contraseña del usuario administrador:
- Usuario: `LuisMolina`
- Contraseña inicial: `Mathiasmc`

### 4. Base de datos persistente (IMPORTANTE)

El archivo JSON actual (`empleados_data.json`) puede perderse en algunos servicios gratuitos que no tienen almacenamiento persistente.

**Soluciones:**

#### A. Para Render.com:
- Usar "Disk" persistente (opción en el dashboard)
- O migrar a PostgreSQL (Render lo ofrece gratis)

#### B. Para Railway:
- Los archivos se mantienen por defecto
- O usar Railway PostgreSQL

#### C. Para PythonAnywhere:
- Los archivos son persistentes por defecto ✅

#### D. Opción avanzada - Migrar a SQLite:
Consulta la documentación para migrar de JSON a SQLite para mayor persistencia y rendimiento.

---

## Pasos Después del Deployment

1. **Probar acceso**
   - Abre la URL de tu app
   - Verifica que puedes iniciar sesión

2. **Cambiar contraseña admin**
   - Accede con las credenciales iniciales
   - Ve a Ajustes → Cambiar contraseña

3. **Configurar dominio personalizado (opcional)**
   - La mayoría de servicios permite conectar tu dominio propio
   - Ejemplo: `empleados.tuempresa.com`

4. **Monitoreo**
   - Configura alertas de uptime (ej: UptimeRobot)
   - Revisa logs regularmente en tu dashboard

---

## Recomendación Final

**Para máxima facilidad + seguridad + gratis:**
→ **Render.com** es la mejor opción

- ✅ Gratis
- ✅ HTTPS automático
- ✅ Activo 24/7
- ✅ Fácil de configurar
- ✅ Despliegues automáticos desde Git
- ✅ Soporte de disco persistente

**URL de ejemplo:** `https://sistema-empleados.onrender.com`

Tu equipo podrá acceder desde cualquier dispositivo, en cualquier red, sin necesidad de que tu equipo esté encendido.

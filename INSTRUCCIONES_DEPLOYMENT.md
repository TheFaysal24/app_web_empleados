# 🚀 Instrucciones para Deployment - PASO A PASO

## ✅ PASO 1: Subir a GitHub (YA CASI LISTO)

El código ya está preparado y commiteado localmente. Ahora necesitas:

### 1.1 Subir los cambios a GitHub

Abre una terminal (PowerShell o CMD) en la carpeta del proyecto y ejecuta:

```bash
git push origin main
```

**Si te pide usuario y contraseña:**
- Usuario: `TheFaysal24`
- Contraseña: Usa un **Personal Access Token** de GitHub (no tu contraseña normal)

### 1.2 Crear Personal Access Token (si lo necesitas)

1. Ve a: https://github.com/settings/tokens
2. Click en **"Generate new token"** → **"Generate new token (classic)"**
3. Nombre: `Render Deploy Token`
4. Expiration: **No expiration** (o 1 año)
5. Selecciona scope: ✅ **repo** (todos los checkboxes)
6. Click **"Generate token"**
7. **COPIA EL TOKEN** (solo se muestra una vez) - algo como `ghp_xxxxxxxxxxxx`
8. Úsalo como contraseña cuando hagas `git push`

---

## ✅ PASO 2: Desplegar en Render.com (GRATIS Y SEGURO)

### 2.1 Crear cuenta en Render

1. Ve a: **https://render.com**
2. Click en **"Get Started for Free"**
3. **Regístrate con tu cuenta de GitHub** (más fácil)
4. Autoriza a Render a acceder a tus repositorios

### 2.2 Crear nuevo Web Service

1. En el dashboard de Render, click **"New +"** → **"Web Service"**
2. Click **"Connect a repository"**
3. Busca y selecciona: **`app_web_empleados`**
4. Click **"Connect"**

### 2.3 Configurar el servicio

**Nombre del servicio:**
```
sistema-empleados
```
(o el nombre que prefieras, esto será parte de tu URL)

**Región:**
```
Frankfurt (EU Central)
```
(o la más cercana a ti)

**Branch:**
```
main
```

**Root Directory:** (dejar en blanco)

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn app:app
```

**Instance Type:**
```
Free
```

### 2.4 Variables de Entorno

En la sección **"Environment Variables"**, click **"Add Environment Variable"**:

**Key:**
```
SECRET_KEY
```

**Value:** (genera una clave segura)
```
tu-clave-super-secreta-larga-y-aleatoria-12345
```

💡 **Mejor aún, genera una aleatoria:**
- Ve a: https://randomkeygen.com/
- Copia una de las claves "Fort Knox Passwords"
- O usa esta temporal: `8f9a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8`

### 2.5 Disco Persistente (IMPORTANTE)

Para que no pierdas los datos cuando Render reinicie:

1. Scroll hasta **"Disks"**
2. Click **"Add Disk"**
3. **Name:** `data`
4. **Mount Path:** `/opt/render/project/src`
5. **Size:** `1 GB` (gratis)

### 2.6 Deploy!

1. Click **"Create Web Service"**
2. Render comenzará a construir y desplegar tu app
3. Espera 3-5 minutos
4. Verás logs en tiempo real

### 2.7 URL de tu aplicación

Una vez desplegada, tu URL será:
```
https://sistema-empleados.onrender.com
```

✅ **HTTPS automático** (seguro)
✅ **Activo 24/7**
✅ **Accesible desde cualquier dispositivo**

---

## ✅ PASO 3: Probar tu aplicación

1. Abre la URL en tu navegador
2. Verás la página de inicio
3. Click en **"Iniciar Sesión"**
4. Usa las credenciales:
   - **Usuario:** `LuisMolina`
   - **Contraseña:** `Mathiasmc`

### 3.1 Cambiar contraseña del admin (IMPORTANTE)

1. Una vez dentro, ve a **Ajustes** → **Cambiar Contraseña**
2. Cambia la contraseña por una segura
3. ¡Listo! Ya puedes usar el sistema

---

## ✅ PASO 4: Compartir con tu equipo

Simplemente comparte la URL:
```
https://sistema-empleados.onrender.com
```

Todos podrán acceder desde:
- 💻 Computadoras (Windows, Mac, Linux)
- 📱 Celulares (Android, iPhone)
- 📟 Tablets
- 🌐 Desde cualquier red WiFi o datos móviles

**SIN necesidad de que tu equipo esté encendido** ✅

---

## 🔄 Actualizar la aplicación (si haces cambios)

Cuando hagas cambios en el código:

```bash
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

Render detectará el cambio y **desplegará automáticamente** la nueva versión.

---

## 🆘 Problemas Comunes

### Error: "Application failed to respond"

**Solución:** Verifica que el archivo `Procfile` exista y contenga:
```
web: gunicorn app:app
```

### Error: "No module named 'gunicorn'"

**Solución:** Verifica que `requirements.txt` contenga:
```
Flask==2.3.3
gunicorn==21.2.0
Werkzeug==2.3.7
```

### La aplicación se reinicia y pierde datos

**Solución:** Agrega un disco persistente (ver paso 2.5)

### No puedo hacer push a GitHub

**Solución:** Usa un Personal Access Token en lugar de tu contraseña (ver paso 1.2)

---

## 📞 Contacto y Soporte

Si tienes problemas:
1. Revisa los **logs en Render** (pestaña "Logs")
2. Verifica que todas las variables de entorno estén configuradas
3. Contacta: lemolina0323@gmail.com

---

## 🎉 ¡Felicidades!

Tu sistema de empleados ahora está:
- ✅ En la nube
- ✅ Con HTTPS (seguro)
- ✅ Accesible 24/7
- ✅ Sin límites de dispositivos
- ✅ Gratis

**URL final:** https://sistema-empleados.onrender.com

¡Disfruta de tu sistema! 🚀

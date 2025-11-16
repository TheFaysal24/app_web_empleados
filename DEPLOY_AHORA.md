# 🚀 TU CÓDIGO YA ESTÁ EN GITHUB ✅

## Repositorio actualizado:
**https://github.com/TheFaysal24/app_web_empleados**

---

# AHORA SIGUE ESTOS PASOS PARA TENER TU URL PÚBLICA:

## 📝 PASO 1: Crear cuenta en Render

1. **Abre:** https://render.com
2. **Click en:** "Get Started for Free"
3. **Selecciona:** "Sign in with GitHub" (es más rápido)
4. **Autoriza** a Render para acceder a tus repositorios

---

## 🔧 PASO 2: Crear el Web Service

1. En el dashboard de Render, click en **"New +"** (arriba a la derecha)
2. Selecciona **"Web Service"**
3. Click en **"Connect a repository"**
4. Busca **"app_web_empleados"** en la lista
5. Click en **"Connect"** al lado del repositorio

---

## ⚙️ PASO 3: Configurar (IMPORTANTE - COPIA EXACTO)

Llena el formulario con estos datos:

### Name (Nombre de tu app):
```
sistema-empleados
```
Este será parte de tu URL final: `sistema-empleados.onrender.com`

### Region:
```
Frankfurt (EU Central)
```
(O selecciona la más cercana a ti)

### Branch:
```
main
```

### Runtime:
```
Python 3
```

### Build Command:
```
pip install -r requirements.txt
```

### Start Command:
```
gunicorn app:app
```

### Instance Type:
```
Free
```

---

## 🔐 PASO 4: Agregar Variable de Entorno (CRÍTICO)

Scroll hacia abajo hasta "Environment Variables" y click en **"Add Environment Variable"**:

**Key:**
```
SECRET_KEY
```

**Value:** (copia esta clave - ya está generada para ti)
```
8f9a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c
```

---

## 💾 PASO 5: Disco Persistente (Para NO perder datos)

Scroll más abajo hasta encontrar **"Disks"** y click en **"Add Disk"**:

**Name:**
```
data
```

**Mount Path:**
```
/opt/render/project/src
```

**Size:**
```
1 GB
```
(Es gratis)

---

## 🚀 PASO 6: DEPLOY!

1. Click en **"Create Web Service"** (botón azul al final)
2. Render empezará a construir tu aplicación
3. Verás logs en tiempo real (tarda 3-5 minutos)
4. Espera a que diga **"Live"** con un punto verde ✅

---

## 🌐 PASO 7: TU URL ESTARÁ LISTA

Tu aplicación estará disponible en:

```
https://sistema-empleados.onrender.com
```

O el nombre que hayas elegido en el Paso 3.

### ¡COMPARTE ESA URL con tu equipo!

Todos podrán acceder desde cualquier dispositivo, en cualquier lugar del mundo:
- ✅ Computadoras
- ✅ Celulares
- ✅ Tablets
- ✅ Sin necesidad de que TU equipo esté encendido

---

## 🔑 PRIMERA VEZ - Credenciales de Admin

Cuando accedas por primera vez:

**Usuario:**
```
LuisMolina
```

**Contraseña:**
```
Mathiasmc
```

⚠️ **IMPORTANTE:** Una vez dentro, ve a **Gestión de Usuarios** → **Cambiar Contraseña** para cambiarla por una segura.

---

## 📱 Crear Usuarios para tu Equipo

1. Como admin, ve a la URL de tu app
2. Tus empleados pueden hacer click en **"Crear Cuenta"**
3. O tú puedes crearlas desde **Gestión de Usuarios**

Cada empleado tendrá:
- Su propio usuario y contraseña
- Acceso SOLO para marcar inicio/salida
- Ver sus propios registros

Tú como admin puedes:
- Ver todos los registros
- Editar/borrar registros
- Cambiar contraseñas
- Bloquear/desbloquear usuarios
- Exportar datos a Excel (CSV)

---

## 🔄 Si Haces Cambios en el Futuro

Cuando modifiques algo en el código:

```bash
git add .
git commit -m "Descripción del cambio"
git push origin main
```

Render detectará el cambio y **desplegará automáticamente** la nueva versión.

---

## 🆘 ¿Problemas?

Si algo no funciona:

1. **Verifica los logs** en Render (pestaña "Logs")
2. **Comprueba** que agregaste la variable `SECRET_KEY`
3. **Espera** 5 minutos - a veces tarda un poco
4. **Revisa** que el disco persistente esté agregado

---

## 🎉 ¡LISTO!

Tu sistema de gestión de empleados ahora está:

✅ En la nube (Render.com)
✅ Con HTTPS (conexión segura)
✅ Disponible 24/7
✅ Accesible desde cualquier lugar
✅ GRATIS
✅ Sin límite de usuarios

**Repositorio GitHub:** https://github.com/TheFaysal24/app_web_empleados
**URL de la app:** https://sistema-empleados.onrender.com

---

## 📞 Contacto

- **Email:** lemolina0323@gmail.com
- **GitHub:** TheFaysal24

¡Disfruta de tu sistema! 🚀

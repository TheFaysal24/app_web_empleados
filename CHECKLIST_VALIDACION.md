# ✅ CHECKLIST DE VALIDACIÓN - Sistema Desplegado

## 📋 Verificaciones Necesarias

### 1️⃣ Obtener la URL de tu aplicación

En el dashboard de Render, deberías ver:
- Un punto verde ✅ que dice "Live"
- Una URL como: `https://app-web-empleados.onrender.com` o similar

**Copia esa URL completa**

---

### 2️⃣ Verificar Variables de Entorno

**CRÍTICO:** Asegúrate de que la variable SECRET_KEY esté configurada:

1. En Render, ve a tu servicio (click en el nombre)
2. Click en "Environment" en el menú lateral
3. Verifica que exista:
   - **Key:** `SECRET_KEY`
   - **Value:** (una clave larga)

**Si NO está:**
1. Click en "Add Environment Variable"
2. Key: `SECRET_KEY`
3. Value: `8f9a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c`
4. Guarda y espera que redepliegue (2-3 minutos)

---

### 3️⃣ Verificar Disco Persistente

Para que NO pierdas los datos cuando Render reinicie:

1. En tu servicio, ve a "Disks" en el menú lateral
2. Debería haber un disco configurado:
   - Name: `data`
   - Mount Path: `/opt/render/project/src`

**Si NO está:**
1. Click en "Add Disk"
2. Name: `data`
3. Mount Path: `/opt/render/project/src`
4. Size: `1 GB`
5. Guarda

---

### 4️⃣ Probar el Login

1. Abre la URL de tu app en el navegador
2. Deberías ver la página de inicio elegante con gradiente animado
3. Click en "Iniciar Sesión"
4. Usa estas credenciales:
   - **Usuario:** `LuisMolina`
   - **Contraseña:** `Mathiasmc`

**✅ Si entras:** ¡Funciona perfecto!
**❌ Si no cargas:** Verifica los logs en Render

---

### 5️⃣ Cambiar Contraseña del Admin

**IMPORTANTE - Hazlo ahora:**

1. Una vez dentro, ve a "Gestión de Usuarios"
2. Click en "Cambiar Contraseña" para el usuario LuisMolina
3. Ingresa una contraseña segura nueva
4. Guarda

---

### 6️⃣ Probar Funcionalidades

- ✅ Marcar inicio de jornada
- ✅ Marcar salida de jornada
- ✅ Ver registros en el dashboard
- ✅ Crear un usuario de prueba
- ✅ Exportar datos a CSV

---

## 🆘 Si Algo No Funciona

### Error: "Application Error" o página en blanco

**Solución:**
1. Ve a tu servicio en Render
2. Click en "Logs" (menú lateral)
3. Busca errores en rojo
4. Copia el error y dímelo

### Error: "ModuleNotFoundError: No module named 'gunicorn'"

**Solución:**
1. Verifica que `requirements.txt` tenga:
   ```
   Flask==2.3.3
   gunicorn==21.2.0
   Werkzeug==2.3.7
   ```
2. Si falta, agrégalo y haz:
   ```bash
   git add requirements.txt
   git commit -m "Agregar gunicorn"
   git push origin main
   ```

### La página carga pero no guarda datos

**Solución:** Falta el disco persistente (ver paso 3 arriba)

---

## 📱 Compartir con tu Equipo

Una vez validado, comparte la URL:

**Ejemplo:**
```
https://app-web-empleados.onrender.com
```

Tus empleados pueden:
1. Abrir esa URL desde cualquier dispositivo
2. Click en "Crear Cuenta"
3. Llenar sus datos
4. Empezar a marcar asistencia

---

## 🎉 Todo OK? Tu Sistema está:

✅ En producción
✅ Con HTTPS seguro
✅ Accesible 24/7 desde cualquier lugar
✅ Gratis
✅ Con datos persistentes
✅ Listo para usar

---

**¿Necesitas ayuda con algo específico?**

# 🚀 GUÍA DE DESPLIEGUE FINAL - RENDER

## ✅ TODO LISTO EN GITHUB
Repositorio: **https://github.com/TheFaysal24/app_web_empleados**

## 🎯 DEPLOY EN RENDER (5 MINUTOS)

### Paso 1: Accede a Render
1. Ve a: **https://render.com**
2. Click en **"Get Started for Free"**
3. **Login con GitHub**

### Paso 2: Crear Web Service
1. Click en **"New +"** → **"Web Service"**
2. Click en **"Connect account"** si no has conectado GitHub
3. Busca y selecciona: **TheFaysal24/app_web_empleados**
4. Click en **"Connect"**

### Paso 3: Configuración EXACTA

```
Name: app-web-empleados
Region: Oregon (US West)
Branch: main
Root Directory: (VACÍO)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

### Paso 4: Variables de Entorno

Click en **"Advanced"** y agrega:

```
SECRET_KEY: genera_una_clave_aleatoria_segura_123456
PYTHON_VERSION: 3.11.0
```

### Paso 5: Deploy

1. Selecciona plan: **Free**
2. Click en **"Create Web Service"**
3. **Espera 3-5 minutos**

¡LISTO! Render te dará una URL:
```
https://app-web-empleados.onrender.com
```

---

## 🔐 CREDENCIALES DE ACCESO

### Administrador
- Usuario: `admin`
- Contraseña: `1234`

### Gestores Operativos
- `natalia.arevalo` - Contraseña: `1234` - Cédula: 1070963486
- `lesly.guzman` - Contraseña: `1234` - Cédula: 1067949514
- `paola.garcia` - Contraseña: `1234` - Cédula: 1140870406
- `dayana.gonzalez` - Contraseña: `1234` - Cédula: 1068416077

**⚠️ CAMBIAR CONTRASEÑAS DESPUÉS DEL PRIMER ACCESO**

---

## 📊 CARACTERÍSTICAS IMPLEMENTADAS

### Para Administrador:
✅ Panel de Gestión Ejecutiva (sin botones Inicio/Salida)
✅ Asignación manual de turnos a cualquier gestor
✅ Edición completa de usuarios (nombre, cédula, cargo, contraseña, permisos)
✅ Modificación de registros de asistencia
✅ Eliminación de usuarios y turnos
✅ Gráficos financieros (costos de horas extras)
✅ Resumen semanal con cédulas
✅ Backups y exportación CSV
✅ Menú hamburguesa elegante

### Para Gestores Operativos:
✅ Botones Inicio/Salida de turnos
✅ Widgets de acceso rápido a módulos
✅ Selección de turnos según su patrón por cédula
✅ Eliminación de turnos propios
✅ Ver historial de turnos asignados
✅ Módulo de turnos con trazabilidad desde Nov 3, 2025
✅ NO ven costos ni horas extras (solo horas trabajadas)

### Sistema de Turnos:
✅ Rotación automática por cédula
✅ Historial mensual persistente (no se sobrescribe)
✅ Asignación inteligente sin repetir turnos
✅ Cálculo correcto de horas (descontando almuerzo)
✅ Registro desde Nov 3, 2025

---

## 🔄 ACTUALIZACIONES AUTOMÁTICAS

Cada `git push` a `main` redespliega automáticamente en Render.

---

## 🛠 SI HAY PROBLEMAS

### Ver logs:
1. En Render → tu servicio → pestaña **"Logs"**

### Errores comunes resueltos:
✅ Templates con mayúscula → configurado `template_folder='Templates'`
✅ Rutas duplicadas → eliminadas
✅ Respuestas JSON → corregidas con `jsonify()`
✅ Validaciones None → agregadas en todos los templates

---

## 📱 SIGUIENTE: PRUEBA LOCAL

Antes de desplegar, prueba local:
```bash
python app.py
```

Accede a: `http://127.0.0.1:5000`

Si funciona local, funcionará en Render! 🎉

---

**¿LISTO PARA DESPLEGAR?** → Ve a https://render.com y sigue los 5 pasos arriba.

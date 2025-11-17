# ⚡ INSTALACIÓN RÁPIDA - 5 MINUTOS

## 🎯 INICIO RÁPIDO

### Opción 1: Instalación Automática (Recomendado)

```bash
# 1. Navegar al directorio
cd app_web_empleados

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar entorno
python -c "import os; open('.env', 'w').write(f'SECRET_KEY={os.urandom(24).hex()}\nEMAIL_PASSWORD=')"

# 4. Migrar contraseñas (opcional)
python migrar_passwords.py

# 5. Ejecutar
python app.py
```

### Opción 2: Instalación Manual

#### Paso 1: Dependencias (1 min)
```bash
pip install Flask==2.3.3
pip install Flask-Login==0.6.3
pip install Flask-Limiter==3.5.0
pip install Flask-WTF==1.2.1
pip install Werkzeug==2.3.7
pip install python-dotenv==1.0.0
pip install gunicorn==21.2.0
```

#### Paso 2: Archivo .env (30 seg)
Crear archivo `.env` en la raíz:
```env
SECRET_KEY=tu_clave_super_secreta_aqui_minimo_32_caracteres_aleatorios_12345678
EMAIL_PASSWORD=tu_password_de_aplicacion_gmail
```

**Generar SECRET_KEY segura:**
```bash
python -c "import os; print(os.urandom(24).hex())"
```

#### Paso 3: Ejecutar (10 seg)
```bash
python app.py
```

#### Paso 4: Acceder
Abrir navegador: **http://localhost:5000**

---

## 🔐 CREDENCIALES DEFAULT

**Administrador:**
- Usuario: `LuisMolina`
- Contraseña: `Mathiasmc`

**⚠️ IMPORTANTE**: Cambiar contraseña después del primer login

---

## ✅ VERIFICACIÓN

### Checklist Post-Instalación

- [ ] Aplicación corre sin errores
- [ ] Puedes hacer login
- [ ] Archivo `app.log` se crea
- [ ] Módulo turnos mensual accesible
- [ ] Botones tienen nuevo diseño
- [ ] No hay errores en consola

### Comandos de Verificación

```bash
# Verificar dependencias
pip list | grep Flask

# Verificar archivo .env
cat .env  # Linux/Mac
type .env  # Windows

# Ver logs
tail -f app.log  # Linux/Mac
Get-Content app.log -Tail 10  # Windows PowerShell
```

---

## 🚀 ACCESO RÁPIDO

### Rutas Principales

```
/                     → Home
/login               → Login
/register            → Registro
/dashboard           → Dashboard Principal
/turnos_mensual      → Módulo Turnos Mensual (NUEVO)
/admin/usuarios      → Gestión Usuarios (Admin)
```

### Navegación Rápida

**Desde Dashboard:**
- Ver Turnos Mensual
- Marcar Asistencia
- Exportar Datos (Admin)
- Gestionar Usuarios (Admin)

---

## 🎨 CARACTERÍSTICAS NUEVAS

### 1. Hash de Contraseñas ✅
```
Login → Migración automática a hash
```

### 2. Diseño Moderno ✅
```
Todos los botones → Gradientes 3D
Colores → Paleta profesional
Animaciones → Suaves y elegantes
```

### 3. Turnos Mensual ✅
```
/turnos_mensual → Panel completo
- Vista por gestor
- Límite 20/mes
- Progreso visual
- Historial completo
```

---

## 🔧 TROUBLESHOOTING RÁPIDO

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "SECRET_KEY not found"
```bash
echo "SECRET_KEY=$(python -c 'import os; print(os.urandom(24).hex())')" > .env
```

### Error: "Permission denied"
```bash
# Windows
python -m pip install --user -r requirements.txt

# Linux/Mac
sudo pip install -r requirements.txt
```

### Contraseña no funciona
1. Usa "Recuperar Contraseña"
2. O contacta admin para reset

### Puerto 5000 ocupado
```bash
# Windows
netstat -ano | findstr :5000
taskkill /F /PID <PID>

# Linux/Mac
lsof -i :5000
kill -9 <PID>

# O cambiar puerto
python app.py  # Editar PORT en código
```

---

## 📦 ESTRUCTURA FINAL

```
app_web_empleados/
├── app.py                          ⭐ Principal
├── requirements.txt                📦 Dependencias
├── .env                           🔐 Config (CREAR)
├── .env.example                   📋 Plantilla
├── migrar_passwords.py            🔄 Migración
├── empleados_data.json            💾 Datos
├── app.log                        📝 Logs (AUTO)
├── Templates/
│   ├── turnos_mensual.html        ⭐ NUEVO
│   └── ... (otros templates)
├── static/
│   ├── modern-design.css          ⭐ NUEVO
│   └── ... (otros estáticos)
├── backups/                       💾 Backups
├── RESUMEN_EJECUTIVO.md           📊 Resumen
├── MEJORAS_IMPLEMENTADAS.md       📖 Docs técnica
├── GUIA_VISUAL_MEJORAS.md         🎨 Guía visual
└── INSTALACION_RAPIDA.md          ⚡ Este archivo
```

---

## 🎯 PRIMEROS PASOS DESPUÉS DE INSTALAR

### 1. Login
```
http://localhost:5000/login
Usuario: LuisMolina
Contraseña: Mathiasmc
```

### 2. Cambiar Contraseña
```
Dashboard → Ajustes → Cambiar Contraseña
```

### 3. Explorar Turnos Mensual
```
Dashboard → Turnos Mensual
```

### 4. Crear Usuarios
```
Dashboard → Admin → Gestión Usuarios
```

### 5. Revisar Logs
```
Abrir: app.log
```

---

## 🚀 DEPLOYMENT PRODUCCIÓN

### Render.com (Recomendado)

```bash
# 1. Subir a GitHub
git init
git add .
git commit -m "Sistema con mejoras v2.0"
git push origin main

# 2. En Render.com
- New Web Service
- Connect repository
- Build: pip install -r requirements.txt
- Start: gunicorn app:app
- Environment: Agregar SECRET_KEY

# 3. Deploy automático ✅
```

### Variables de Entorno en Render
```
SECRET_KEY = tu_clave_super_secreta_aqui
EMAIL_PASSWORD = tu_password_gmail
```

---

## 📞 SOPORTE RÁPIDO

### ¿No funciona?
1. Verifica Python 3.8+: `python --version`
2. Reinstala dependencias: `pip install -r requirements.txt`
3. Revisa `.env` existe y tiene SECRET_KEY
4. Consulta `app.log` para errores

### ¿Necesitas ayuda?
1. Lee `GUIA_VISUAL_MEJORAS.md`
2. Consulta `MEJORAS_IMPLEMENTADAS.md`
3. Revisa código comentado

---

## ✅ CHECKLIST COMPLETO

### Instalación
- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas
- [ ] Archivo `.env` creado
- [ ] SECRET_KEY configurada

### Verificación
- [ ] `python app.py` ejecuta sin errores
- [ ] Login funciona
- [ ] Dashboard carga correctamente
- [ ] Turnos mensual accesible
- [ ] Logs se generan

### Post-Instalación
- [ ] Contraseña admin cambiada
- [ ] Usuarios de prueba creados
- [ ] Turnos asignados
- [ ] Backup configurado

---

## 🎉 FELICIDADES!

Tu sistema está listo con:
- ✅ Seguridad nivel producción
- ✅ Diseño profesional moderno
- ✅ Módulo de turnos avanzado
- ✅ Logging y auditoría
- ✅ Listo para escalar

**Próximo paso**: Explorar y disfrutar 🚀

---

## 📚 DOCUMENTACIÓN COMPLETA

- `RESUMEN_EJECUTIVO.md` - Resumen de mejoras
- `MEJORAS_IMPLEMENTADAS.md` - Documentación técnica
- `GUIA_VISUAL_MEJORAS.md` - Guía visual paso a paso
- `README.md` - Documentación general

---

**Tiempo estimado**: ⏱️ 5 minutos  
**Dificultad**: 🟢 Fácil  
**Estado**: ✅ Listo para usar  

*¡Disfruta tu nuevo sistema mejorado!* 🎊

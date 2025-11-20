# 🔧 TROUBLESHOOTING GUIDE

## Si encuentras errores, sigue estos pasos

---

## ❌ Error: "ModuleNotFoundError: No module named 'flask'"

### Causa
Flask no está instalado en tu Python

### Solución
```bash
pip install -r requirements.txt
```

### Verifica
```bash
python -c "import flask; print(flask.__version__)"
```
Deberías ver: `2.3.3`

---

## ❌ Error: "FileNotFoundError: [Errno 2] No such file or directory: '.env'"

### Causa
No existe archivo `.env`

### Solución
```bash
cp .env.example .env
```

### Luego edita `.env` con tu editor:
```
DB_PASSWORD=tu_contraseña_postgres
SECRET_KEY=tu_clave_secreta
```

---

## ❌ Error: "psycopg2.OperationalError: could not connect to server"

### Causa
PostgreSQL no está corriendo o credenciales inválidas

### Solución Opción 1: Verificar PostgreSQL
```bash
# Windows
# Abre Services (servicios) y busca PostgreSQL
# O en Terminal:
pg_isready -h localhost -p 5432
```

### Solución Opción 2: Verificar Credenciales
En `.env` revisa:
```
DB_HOST=localhost      # ¿Es correcto?
DB_USER=postgres       # ¿Es tu usuario?
DB_PASSWORD=???        # ¿Es tu contraseña?
DB_NAME=sistema_empleados  # ¿Existe esta BD?
```

### Crear BD si no existe
```bash
# En PostgreSQL
createdb sistema_empleados
```

---

## ❌ Error: "CSRF token missing"

### Causa
El formulario no tiene el token CSRF

### Solución
Abre el template (ej: `dashboard.html`) y busca:
```html
<form method="POST">
```

Debajo de esa línea agrega:
```html
<form method="POST">
  {{ csrf_token() }}
  <!-- resto del formulario -->
</form>
```

### Verifica
Recarga la página (Ctrl+F5) y prueba el formulario

---

## ❌ Error: "werkzeug.exceptions.BadRequest: 400 Bad Request"

### Causa
Datos inválidos o token CSRF faltante

### Solución
1. Verifica que el formulario tenga `{{ csrf_token() }}`
2. Limpia el navegador (Ctrl+Shift+Delete - cookies/cache)
3. Recarga (Ctrl+F5)
4. Intenta de nuevo

---

## ❌ Error: "ValueError: Email inválido"

### Causa
El email no es válido según nuestras reglas

### Validación de Email
✅ **Válidos**:
- juan@empresa.com
- j.perez@empresa.com
- juan+reports@empresa.com

❌ **Inválidos**:
- juanemail.com (sin @)
- juan@.com (sin dominio)
- @empresa.com (sin usuario)

### Solución
Usa un email en formato correcto: `usuario@dominio.com`

---

## ❌ Error: "ValueError: Cédula inválida"

### Causa
La cédula no tiene el formato correcto

### Validación de Cédula
✅ **Válidas**:
- 1234567890 (solo números, 8-15 dígitos)
- 12345678
- 1234567890123456

❌ **Inválidas**:
- 123-456-7890 (contiene guiones)
- ABC1234567 (contiene letras)
- 123 (menos de 8 dígitos)

### Solución
Ingresa solo números, entre 8 y 15 dígitos

---

## ❌ Error: "ValueError: Username inválido"

### Causa
El username no cumple con los requisitos

### Validación de Username
✅ **Válidos**:
- juan_perez (3-50 caracteres)
- juan-perez (con guiones)
- juanperez123
- juan_perez_2025

❌ **Inválidos**:
- ju (menos de 3 caracteres)
- juan perez (contiene espacio)
- juan@perez (contiene @)
- juan.perez (contiene punto) ← Aunque funciona, mejor evitar

### Solución
Usa: letras, números, guiones (_) y subguiones (-), mínimo 3 caracteres

---

## ❌ Error: "Internal Server Error" (Error 500)

### Causa
Error interno de la aplicación

### Solución Paso a Paso
1. **Revisa el archivo `app.log`**
   ```bash
   tail -50 app.log  # Últimas 50 líneas
   ```

2. **Busca el error específico** (línea roja en el log)

3. **Problemas comunes:**
   - Database connection failed → verifica `.env`
   - Template not found → verifica ruta de template
   - Key error → falta variable en render_template()

4. **Reinicia la app**
   ```bash
   # Ctrl+C en la terminal
   python app.py  # Ejecuta de nuevo
   ```

---

## ❌ Error: "Template not found: dashboard.html"

### Causa
Está en carpeta incorrecta o mal nombrado

### Solución
1. Verifica que exista: `Templates/dashboard.html`
2. Nota la **T mayúscula** en "Templates" (es importante)
3. Verifica que el archivo no tenga espacio en blanco al inicio

### Estructura Correcta
```
app_web_empleados/
├── app.py
├── Templates/
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   └── ... más templates
└── static/
```

---

## ❌ Error: "Database table already exists"

### Causa
Intento de crear tabla que ya existe

### Solución
Es normal, Flask maneja esto automáticamente con `CREATE TABLE IF NOT EXISTS`

Si ves el error, simplemente **reinicia la app**, que lo manejará.

---

## ⚠️ Advertencia: "ADVERTENCIA: Usando SECRET_KEY por defecto"

### Significa
No configuraste SECRET_KEY en `.env`

### Solución
En `.env` agrega:
```
SECRET_KEY=tu_clave_super_secreta_aqui_minimo_32_caracteres
```

### Generar clave segura
```bash
python -c "import os; print(os.urandom(32).hex())"
```

Copia el resultado en `SECRET_KEY=`

---

## 🔍 DEBUGGING TIPS

### Ver logs en tiempo real
```bash
tail -f app.log
```
(Mostrará logs a medida que ocurran)

### Activar modo debug (solo desarrollo)
En `app.py` (línea con `app.run()`):
```python
app.run(debug=True)  # Permite recargar automáticamente
```

### Verificar BD
```bash
psql -U postgres -d sistema_empleados
\dt  # Mostrar todas las tablas
SELECT * FROM usuarios LIMIT 5;  # Ver usuarios
```

### Limpiar cache del navegador
- **Windows**: Ctrl+Shift+Delete
- **Mac**: Cmd+Shift+Delete
- **Linux**: Ctrl+Shift+Delete

---

## ✅ VERIFICACIÓN COMPLETA

Si todo funciona, deberías ver:

1. **Login page carga** ✅
2. **Puedes hacer login** ✅
3. **Dashboard carga** ✅
4. **Ves horarios de entrada/salida** ✅
5. **Ves turnos seleccionados** ✅
6. **Registro de nuevos usuarios funciona** ✅
7. **No hay errores en `app.log`** ✅

---

## 📞 OBTENER AYUDA

### Revisa primero:
1. `app.log` - Línea del error
2. `MEJORAS_IMPLEMENTADAS_19NOV.md` - Detalles técnicos
3. `GUIA_RAPIDA_MEJORAS.md` - Guía de uso

### Si nada funciona:
1. Revisa todos los pasos en "GUIA_RAPIDA_MEJORAS.md"
2. Copia el error exacto de `app.log`
3. Verifica que `.env` esté configurado correctamente
4. Intenta:`python app.py` de nuevo

---

**¡Buena suerte! 🍀 Cualquier problema, revisa los logs primero.**

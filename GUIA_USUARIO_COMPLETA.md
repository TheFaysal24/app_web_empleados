# 📘 GUÍA COMPLETA DEL SISTEMA DE GESTIÓN DE EMPLEADOS

---

## 📋 Manual de Usuario
### Sistema de Control de Asistencia y Gestión de Personal

**Versión:** 1.0  
**Fecha:** Noviembre 2025  
**Desarrollado por:** Luis Molina  
**Contacto:** lemolina0323@gmail.com

---

# TABLA DE CONTENIDOS

1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Guía para Administradores](#guía-para-administradores)
4. [Guía para Empleados](#guía-para-empleados)
5. [Gestión de Backups](#gestión-de-backups)
6. [Recomendaciones de Seguridad](#recomendaciones-de-seguridad)
7. [Solución de Problemas](#solución-de-problemas)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

---

# INTRODUCCIÓN

## ¿Qué es este sistema?

El Sistema de Gestión de Empleados es una aplicación web profesional diseñada para:

✅ **Control de asistencia** - Registrar entrada y salida de empleados  
✅ **Cálculo automático** - Horas trabajadas y horas extras  
✅ **Gestión de personal** - Administración completa de usuarios  
✅ **Reportes** - Exportación de datos a Excel (CSV)  
✅ **Seguridad** - Sistema de roles y permisos  
✅ **Disponibilidad 24/7** - Acceso desde cualquier dispositivo

## Características Principales

### Para Administradores 👑
- Dashboard con estadísticas en tiempo real
- Gestión completa de usuarios
- Cambio de contraseñas de empleados
- Edición y eliminación de registros
- Bloqueo/desbloqueo de cuentas
- Exportación de datos a CSV
- Sistema de backups automáticos

### Para Empleados 📋
- Marcar entrada de jornada
- Marcar salida de jornada
- Visualizar historial personal
- Cambiar propia contraseña
- Ver horas trabajadas y extras

---

# ACCESO AL SISTEMA

## URL del Sistema

**🌐 Dirección Web:**
```
https://app-web-empleados.onrender.com
```

> 💡 **Consejo:** Guarda esta dirección en tus marcadores/favoritos

## Requisitos Técnicos

- ✅ Navegador web moderno (Chrome, Firefox, Edge, Safari)
- ✅ Conexión a internet
- ✅ No requiere instalación de software

## Compatibilidad

El sistema funciona en:
- 💻 Computadoras (Windows, Mac, Linux)
- 📱 Teléfonos móviles (Android, iPhone)
- 📟 Tablets (iPad, Android)

---

# PASO 1: PÁGINA DE INICIO

## ¿Cómo acceder?

1. Abre tu navegador web
2. Escribe: `https://app-web-empleados.onrender.com`
3. Presiona Enter

## ¿Qué verás?

![Pantalla de Inicio]
- Fondo con gradiente animado elegante
- Logo del sistema "Sistema de Empleados"
- Botón **"Iniciar Sesión"**
- Enlace a **"Crear Cuenta"**

## Acciones Disponibles

**Si ya tienes cuenta:**
- Click en **"Iniciar Sesión"**

**Si eres nuevo:**
- Click en **"Crear Cuenta"**

---

# PASO 2: INICIAR SESIÓN

## Pantalla de Login

![Pantalla de Login]
- Diseño moderno con animaciones
- Formulario de inicio de sesión
- Campo de usuario
- Campo de contraseña
- Checkbox "Mantener sesión iniciada"
- Botón "Iniciar Sesión"
- Enlaces adicionales

## ¿Cómo iniciar sesión?

### Paso a Paso:

**1.** Ingresa tu nombre de usuario
   - Ejemplo: `LuisMolina`

**2.** Ingresa tu contraseña
   - La contraseña es sensible a mayúsculas/minúsculas

**3.** (Opcional) Marca "Mantener sesión iniciada"
   - Para no tener que iniciar sesión cada vez

**4.** Click en **"Iniciar Sesión"**

**5.** Si los datos son correctos, serás redirigido al Dashboard

## Credenciales Iniciales del Administrador

**Usuario:** `LuisMolina`  
**Contraseña:** `Mathiasmc`

> ⚠️ **IMPORTANTE:** Cambia esta contraseña después del primer acceso

## ¿Olvidaste tu contraseña?

Click en **"Olvidé mi Contraseña"** debajo del formulario

---

# PASO 3: CREAR CUENTA (Para Nuevos Empleados)

## Pantalla de Registro

![Pantalla de Registro]
- Formulario completo de registro
- Diseño elegante con gradiente coral/turquesa
- Campos de información personal
- Indicador de fortaleza de contraseña

## Datos Requeridos

### Información Personal:
1. **Nombre Completo**
   - Ejemplo: Juan Pérez García

2. **Cédula**
   - Número de identificación

3. **Cargo**
   - Ejemplo: Desarrollador, Contador, Asistente

4. **Correo Electrónico**
   - Ejemplo: juan@empresa.com

### Credenciales de Acceso:
5. **Nombre de Usuario**
   - Sin espacios, puede incluir números
   - Ejemplo: jperez, juan.perez

6. **Contraseña**
   - Mínimo 8 caracteres
   - Se recomienda incluir: mayúsculas, minúsculas, números y símbolos

## Indicador de Contraseña

El sistema muestra la fortaleza de tu contraseña:

- 🔴 **Débil** - Necesita mejoras
- 🟡 **Media** - Aceptable pero puede mejorar
- 🟢 **Fuerte** - Excelente seguridad

## Finalizar Registro

**1.** Completa todos los campos  
**2.** Click en **"Crear Cuenta"**  
**3.** Mensaje de confirmación: "Usuario registrado con éxito"  
**4.** Serás redirigido al Login  
**5.** Inicia sesión con tus nuevas credenciales

---

# GUÍA PARA ADMINISTRADORES

## Dashboard Administrativo

![Dashboard Admin]

### ¿Qué verás al iniciar sesión como admin?

**Sección Superior:**
- Bienvenida personalizada
- Botones rápidos: Marcar Inicio/Salida
- Estadísticas en tiempo real

**Tarjetas de Estadísticas:**
- 👥 Usuarios Iniciados Hoy
- 📊 Total de Inicios de Sesión
- 👤 Nuevos Usuarios
- 💰 Costo Total Horas Extras

**Sección de Gráficos:**
- 📈 Gráfico de horas trabajadas por fecha
- 📊 Estadísticas por empleado

**Tabla de Registros:**
- Listado completo de todos los registros
- Ordenado por fecha
- Opciones de editar/eliminar

## Menú de Navegación

El menú del administrador incluye:

1. **🏠 Inicio** - Dashboard principal
2. **👥 Gestión de Usuarios** - Administrar personal
3. **💾 Gestión de Backups** - Backups automáticos
4. **📤 Exportar Datos** - Descargar CSV
5. **⚙️ Ajustes** - Configuración de cuenta
6. **🚪 Cerrar Sesión** - Salir del sistema

---

# FUNCIONES ADMINISTRATIVAS DETALLADAS

## 1. GESTIÓN DE USUARIOS

### Acceso
**URL:** `https://app-web-empleados.onrender.com/admin/usuarios`

![Gestión de Usuarios]

### ¿Qué puedes hacer?

#### A) Ver Información de Usuarios
Cada tarjeta de usuario muestra:
- Nombre completo
- Usuario
- Rol (Admin/Usuario)
- Estado (Activo/Bloqueado)
- Cédula
- Cargo
- Correo electrónico
- Últimos 5 registros

#### B) Cambiar Contraseña de Usuario

**Paso a Paso:**

1. En la tarjeta del usuario, click en **"Cambiar Contraseña"**
2. Serás redirigido a formulario
3. Ingresa la **nueva contraseña**
4. Click en **"Actualizar Contraseña"**
5. Confirmación: "Contraseña actualizada para [usuario]"

**Cuándo usar:**
- Empleado olvidó su contraseña
- Necesitas resetear acceso de emergencia
- Política de cambio de contraseñas periódicas

#### C) Bloquear/Desbloquear Usuario

**Bloquear Usuario:**
1. Click en botón **"Bloquear"** (amarillo)
2. El usuario NO podrá iniciar sesión
3. Aparecerá badge "🔒 Bloqueado"

**Desbloquear Usuario:**
1. Click en botón **"Desbloquear"** (verde)
2. El usuario recupera acceso
3. Badge desaparece

**Cuándo usar:**
- Suspender temporalmente acceso
- Empleado de vacaciones extendidas
- Medida de seguridad temporal

#### D) Eliminar Usuario

**Paso a Paso:**
1. Click en **"Eliminar Usuario"** (rojo)
2. Confirmación: "¿Estás seguro de eliminar este usuario?"
3. Click en **"Aceptar"**
4. Usuario y TODOS sus registros se eliminan

> ⚠️ **ADVERTENCIA:** Esta acción NO se puede deshacer

**Cuándo usar:**
- Empleado ya no trabaja en la empresa
- Cuenta creada por error
- Limpieza de usuarios inactivos

#### E) Editar Registros de Asistencia

**Desde la tarjeta de usuario:**

1. Localiza el registro en "Registros Recientes"
2. Click en **"Editar"** (botón azul)
3. Modifica:
   - Fecha y hora de inicio
   - Fecha y hora de salida
4. El sistema recalcula automáticamente:
   - Horas trabajadas
   - Horas extras
5. Click en **"Guardar"**

**Cuándo usar:**
- Corregir errores de marcación
- Ajustar horas por eventos especiales
- Regularizar registros incompletos

#### F) Borrar Registros

**Paso a Paso:**
1. En el registro a eliminar, click en **"Borrar"** (rojo)
2. Confirmación: "¿Eliminar este registro?"
3. Click en **"Aceptar"**
4. Registro eliminado permanentemente

**Cuándo usar:**
- Registro duplicado
- Registro creado por error
- Depuración de datos

---

## 2. GESTIÓN DE BACKUPS

### Acceso
**URL:** `https://app-web-empleados.onrender.com/admin/backups`

![Gestión de Backups]

### ¿Qué es un Backup?

Un backup es una **copia de seguridad** de todos los datos del sistema:
- Usuarios registrados
- Todos los registros de asistencia
- Configuraciones del sistema

### Sistema Automático

El sistema crea backups **automáticamente cada 10 días**.

### Información del Backup

**Panel informativo muestra:**
- ⏰ Frecuencia: Cada 10 días
- 📦 Retención: Se mantienen los últimos 10
- 📂 Ubicación: Carpeta `backups/`

> ⚠️ **Sin disco persistente:** Los backups se pierden al reiniciar el servidor (~15 días). **Descárgalos regularmente.**

### Acciones Disponibles

#### A) Ver Lista de Backups

Tabla muestra:
- 📄 Nombre del archivo
- 📅 Fecha de creación
- 💾 Tamaño del archivo
- ⬇️ Botón de descarga

#### B) Crear Backup Manual

**Cuándo crear uno:**
- Antes de hacer cambios importantes
- Antes de eliminar usuarios
- Antes de ediciones masivas
- Fin de mes/período

**Paso a Paso:**
1. Click en **"Crear Backup Ahora"** (botón superior derecho)
2. Mensaje: "Backup creado exitosamente"
3. Aparece en la lista de backups
4. Listo para descargar

#### C) Descargar Backup

**Paso a Paso:**
1. Localiza el backup en la lista
2. Click en **"Descargar"** (botón verde)
3. El archivo se descarga a tu PC
4. Nombre: `empleados_data_backup_YYYYMMDD_HHMMSS.json`

**Dónde guardar los backups:**
- 💻 Tu computadora (carpeta específica)
- ☁️ Google Drive
- ☁️ Dropbox
- 📀 Disco externo

### Recomendaciones de Backup

✅ **Descarga backups CADA SEMANA**  
✅ **Guarda en al menos 2 lugares diferentes**  
✅ **Verifica ocasionalmente que contengan datos**  
✅ **No elimines backups antiguos hasta tener 3+ nuevos**

### Restaurar desde Backup (En caso de emergencia)

Si necesitas restaurar datos:

1. Descarga el backup que quieres restaurar
2. Contacta al soporte técnico: lemolina0323@gmail.com
3. El archivo `.json` será restaurado en el sistema

---

## 3. EXPORTAR DATOS A EXCEL

### Acceso
**URL:** `https://app-web-empleados.onrender.com/exportar_registros`

![Exportar Datos]

### ¿Qué se exporta?

El archivo CSV (compatible con Excel) incluye:

- Usuario
- Nombre completo
- Cédula
- Cargo
- Correo electrónico
- Fecha y hora de inicio
- Fecha y hora de salida
- Horas trabajadas
- Horas extras
- **Costo de horas extras** (calculado automáticamente)

### Cálculo de Horas Extras

El sistema calcula el costo según el día:

**Lunes a Viernes:**
- Horas > 8 = Extras al 125%

**Sábado:**
- Todas las horas = Extras al 175%

**Domingo:**
- Todas las horas = Extras al 200%

**Base de cálculo:**
- Salario mínimo Colombia 2025: $1,384,308
- Valor hora ordinaria: $5,764.61

### ¿Cómo exportar?

**Paso a Paso:**

1. Desde el Dashboard, click en **"Exportar Datos"** o ve directamente a la URL
2. El archivo se descarga automáticamente
3. Nombre: `registros_YYYYMMDD_HHMMSS.csv`
4. Abre con Excel, Google Sheets o LibreOffice

### Usos del archivo exportado

- 📊 Análisis de productividad
- 💰 Cálculo de nómina
- 📈 Reportes gerenciales
- 🧾 Respaldo contable
- 📋 Auditorías

---

## 4. MARCAR INICIO/SALIDA (Admin también puede)

Aunque eres administrador, también puedes marcar tu propia asistencia.

### Marcar Inicio de Jornada

**Desde el Dashboard:**

1. Click en botón **"Marcar Inicio"** (verde)
2. Mensaje: "Hora de inicio registrada"
3. Se guarda automáticamente con fecha y hora actual

### Marcar Salida de Jornada

**Paso a Paso:**

1. Click en botón **"Marcar Salida"** (rojo)
2. El sistema calcula automáticamente:
   - Horas trabajadas
   - Horas extras (si aplica)
3. Mensaje: "Salida registrada. Horas: X.Xh, Extras: X.Xh"

---

# GUÍA PARA EMPLEADOS

## Dashboard de Empleado

![Dashboard Empleado]

### ¿Qué verás al iniciar sesión?

**Sección Superior:**
- Bienvenida personalizada con tu nombre
- Botones: Marcar Inicio / Marcar Salida

**Tus Registros:**
- Tabla con TU historial de asistencia
- Fecha de cada registro
- Hora de inicio
- Hora de salida
- Horas trabajadas
- Horas extras

**Menú:**
- 🏠 Inicio
- ⚙️ Ajustes (cambiar contraseña)
- 🚪 Cerrar Sesión

---

## FUNCIONES DE EMPLEADO

### 1. MARCAR INICIO DE JORNADA

**¿Cuándo marcar?**
- Al llegar al trabajo
- Al comenzar tu turno
- Solo una vez por día

**Paso a Paso:**

1. Inicia sesión en el sistema
2. En el Dashboard, localiza el botón **"Marcar Inicio"** (verde)
3. Click en el botón
4. Mensaje de confirmación: "Hora de inicio registrada"
5. Listo - tu entrada queda registrada

**¿Qué se guarda?**
- Fecha actual
- Hora exacta del registro
- Tu usuario

> 💡 **Nota:** No puedes marcar inicio dos veces el mismo día

### 2. MARCAR SALIDA DE JORNADA

**¿Cuándo marcar?**
- Al terminar tu jornada laboral
- Antes de salir del trabajo

**Paso a Paso:**

1. En el Dashboard, click en **"Marcar Salida"** (rojo)
2. El sistema automáticamente calcula:
   - Total de horas trabajadas
   - Horas extras (si trabajaste más de 8 horas entre semana o 4 el sábado)
3. Mensaje: "Salida registrada. Horas: 8.5h, Extras: 0.5h"
4. Listo

**Importante:**
- ✅ Debes haber marcado inicio primero
- ✅ Solo una salida por día
- ✅ Las horas se calculan automáticamente

### 3. VER TU HISTORIAL

**En tu Dashboard verás:**

Tabla con todos tus registros:

| Fecha | Inicio | Salida | Horas | Extras |
|-------|--------|--------|-------|--------|
| 2025-11-15 | 08:00 | 17:30 | 9.5h | 1.5h |
| 2025-11-14 | 08:15 | 17:00 | 8.75h | 0.75h |

**Colores:**
- 🟢 Verde: Registro completo
- 🟡 Amarillo: Falta marcar salida

### 4. CAMBIAR TU CONTRASEÑA

**Acceso:**
- Menú → **Ajustes**
- URL: `https://app-web-empleados.onrender.com/ajustes`

**Paso a Paso:**

1. Ve a Ajustes
2. Sección "Cambiar Contraseña"
3. Ingresa tu **contraseña actual**
4. Ingresa tu **nueva contraseña**
5. Click en **"Cambiar Contraseña"**
6. Mensaje: "Contraseña actualizada correctamente"

**Recomendaciones de contraseña:**
- Mínimo 8 caracteres
- Incluir mayúsculas y minúsculas
- Incluir números
- Incluir símbolos especiales (@, #, $, etc.)
- No usar información personal obvia

---

## RESTRICCIONES DE EMPLEADO

Como empleado regular, **NO puedes:**

❌ Ver registros de otros empleados  
❌ Editar tus registros pasados  
❌ Eliminar registros  
❌ Cambiar datos personales (nombre, cédula, cargo)  
❌ Acceder a panel de administración  
❌ Ver backups  
❌ Exportar datos

**Solo puedes:**

✅ Marcar tu entrada  
✅ Marcar tu salida  
✅ Ver TU historial personal  
✅ Cambiar TU contraseña

---

# RECOMENDACIONES DE SEGURIDAD

## Para TODOS los Usuarios

### 1. Contraseñas Seguras

✅ **Usa contraseñas fuertes**
- Mínimo 8 caracteres
- Combina mayúsculas, minúsculas, números y símbolos
- Ejemplo: `Emp!2025_Segur@`

❌ **Evita:**
- Nombres propios
- Fechas de nacimiento
- Secuencias simples (123456, abcdef)
- Palabras del diccionario

### 2. No Compartir Credenciales

❌ **Nunca compartas:**
- Tu usuario
- Tu contraseña
- Con compañeros, amigos o familiares

✅ **Si alguien necesita acceso:**
- El admin debe crear una cuenta individual

### 3. Cerrar Sesión

✅ **Siempre cierra sesión cuando:**
- Termines de usar el sistema
- Uses una computadora compartida
- Te ausentes de tu estación de trabajo

**Cómo cerrar sesión:**
- Menú → **"Cerrar Sesión"**
- O click en tu nombre → Cerrar Sesión

### 4. Verificar URL

✅ **Asegúrate de estar en:**
```
https://app-web-empleados.onrender.com
```

❌ **Si la URL es diferente:**
- Puede ser un sitio falso (phishing)
- No ingreses tus credenciales
- Contacta al administrador

### 5. Dispositivos Seguros

✅ **Usa el sistema desde:**
- Tu computadora personal
- Computadora del trabajo
- Tu celular personal

❌ **Evita usar:**
- Computadoras públicas (cibercafés)
- Redes WiFi públicas sin VPN
- Dispositivos de terceros

## Para ADMINISTRADORES

### 1. Cambio de Contraseña Inicial

⚠️ **CRÍTICO:** Cambia la contraseña por defecto INMEDIATAMENTE:

Usuario: `LuisMolina`  
Contraseña: `Mathiasmc` ← **CAMBIAR**

### 2. Backups Regulares

✅ **Descarga backups:**
- Cada semana (mínimo)
- Antes de cambios importantes
- Fin de mes

✅ **Guárdalos en:**
- 2 o más ubicaciones diferentes
- Carpeta dedicada en tu PC
- Servicio en la nube (Google Drive, Dropbox)

### 3. Auditoría de Usuarios

✅ **Revisa periódicamente:**
- Usuarios activos vs. inactivos
- Elimina cuentas de ex-empleados
- Verifica que no haya cuentas duplicadas

### 4. Revisión de Registros

✅ **Monitorea:**
- Registros inconsistentes
- Múltiples inicios en un día (puede ser error)
- Horas trabajadas muy altas o muy bajas

---

# SOLUCIÓN DE PROBLEMAS

## Problema: No puedo iniciar sesión

### Síntoma:
Mensaje "Usuario o contraseña incorrectos"

### Soluciones:

**1. Verifica tus credenciales**
- ¿El usuario está escrito correctamente?
- ¿La contraseña tiene mayúsculas/minúsculas correctas?
- ¿Hay espacios al inicio o final?

**2. CapsLock activado**
- Verifica que no tengas Bloq Mayús activado

**3. Cuenta bloqueada**
- Contacta al administrador
- Puede que tu cuenta esté bloqueada temporalmente

**4. Olvidaste tu contraseña**
- Click en "Olvidé mi Contraseña"
- O contacta al administrador para reseteo

---

## Problema: Ya marqué inicio pero quiero volver a marcar

### Síntoma:
Mensaje "Ya registraste tu inicio hoy"

### Explicación:
El sistema previene marcaciones duplicadas el mismo día.

### Soluciones:

**Si fue un error:**
- Contacta al administrador
- El admin puede eliminar el registro erróneo
- Luego podrás marcar correctamente

**Si necesitas registrar una nueva jornada:**
- Espera al día siguiente
- O el admin puede crear un registro manual

---

## Problema: No veo el botón de Gestión de Usuarios

### Síntoma:
No aparece el menú de administrador

### Causa:
Tu cuenta es de empleado regular, no administrador

### Solución:
Solo los administradores ven estas opciones. Si necesitas acceso de admin, contacta al administrador principal.

---

## Problema: La página no carga o muestra error

### Síntoma:
Pantalla blanca, error 500, o "Application Error"

### Soluciones:

**1. Verifica tu conexión a internet**
- Abre otra página web para verificar
- Reconecta a WiFi si es necesario

**2. Actualiza la página**
- Presiona F5 (Windows) o Cmd+R (Mac)
- O click en el botón de recargar del navegador

**3. Limpia caché del navegador**
- Chrome: Ctrl+Shift+Delete → Borrar datos
- Firefox: Ctrl+Shift+Delete → Limpiar

**4. Intenta con otro navegador**
- Chrome, Firefox, Edge, Safari

**5. Espera unos minutos**
- El servidor puede estar reiniciándose
- Render.com puede tardar 1-2 minutos

**6. Contacta al administrador**
- Si el problema persiste por más de 10 minutos

---

## Problema: No puedo descargar backups

### Síntoma:
Error al hacer click en "Descargar"

### Soluciones:

**1. Verifica que seas administrador**

**2. Verifica que el backup exista**
- Refresh la página
- El backup debe aparecer en la lista

**3. Problemas de navegador**
- Permite descargas en tu navegador
- Verifica que no haya bloqueador de descargas

**4. Crea nuevo backup**
- Click en "Crear Backup Ahora"
- Intenta descargar el nuevo

---

## Problema: Los datos desaparecieron

### Síntoma:
Registros o usuarios faltantes

### Causa Probable:
Render reinició el servidor y no hay disco persistente

### Solución:

**Prevención:**
- Descarga backups regularmente
- Considera agregar disco persistente en Render

**Recuperación:**
- Restaura desde el último backup descargado
- Contacta soporte: lemolina0323@gmail.com
- Provee el archivo de backup

---

# PREGUNTAS FRECUENTES (FAQ)

## ¿Puedo usar el sistema desde mi celular?

**Sí**, el sistema es responsive y funciona perfectamente en:
- 📱 Teléfonos (Android, iPhone)
- 📟 Tablets
- 💻 Computadoras

Solo necesitas un navegador web y conexión a internet.

---

## ¿Necesito internet para marcar asistencia?

**Sí**, el sistema requiere conexión a internet para:
- Acceder al sistema
- Marcar entrada/salida
- Ver registros

Sin internet, no podrás acceder.

---

## ¿Puedo modificar un registro después de marcarlo?

**Empleados:** No, no puedes modificar tus propios registros.

**Administradores:** Sí, pueden editar cualquier registro desde Gestión de Usuarios.

---

## ¿Qué pasa si olvido marcar mi salida?

El registro quedará sin hora de salida. 

**Solución:**
- Contacta al administrador
- El admin puede editar el registro y agregar la hora de salida correcta

---

## ¿Cuánto cuesta usar este sistema?

**Gratis** - El sistema está desplegado en Render.com plan gratuito.

**Limitaciones del plan gratuito:**
- Sin disco persistente (backups temporales)
- Servidor puede hibernar tras inactividad

**Recomendación:**
- Descarga backups semanalmente
- Considera upgrade si crece el equipo

---

## ¿Cuántos usuarios puede manejar el sistema?

No hay límite técnico de usuarios.

**Rendimiento:**
- Plan gratuito: Óptimo hasta 20-30 usuarios
- Para más usuarios, considera plan pago en Render

---

## ¿Cómo se calculan las horas extras?

**Lunes a Viernes:**
- Jornada normal: 8 horas
- Todo lo que exceda 8 horas = horas extras al 125%

**Sábado:**
- Jornada normal: 4 horas
- Todo lo que exceda 4 horas = horas extras al 175%

**Domingo:**
- Todas las horas = extras al 200%

**Cálculo monetario:**
- Base: Salario mínimo Colombia 2025 ($1,384,308)
- Hora ordinaria: $5,764.61
- Hora extra se multiplica por factor del día

---

## ¿Puedo cambiar mi nombre o correo?

**Empleados:** No, solo el administrador puede modificar datos personales.

**Administradores:** Sí, desde Gestión de Usuarios.

**Para solicitar cambio:**
- Contacta al administrador
- Indica qué dato necesitas cambiar

---

## ¿El sistema guarda mi ubicación o IP?

**No**, el sistema solo registra:
- Usuario
- Fecha y hora de entrada/salida
- Horas calculadas

No registra:
- Ubicación GPS
- Dirección IP
- Dispositivo usado

---

## ¿Qué pasa si el administrador olvida su contraseña?

**Solución de emergencia:**
- Contacta soporte técnico: lemolina0323@gmail.com
- Se requerirá verificación de identidad
- Se puede hacer reset manual de la contraseña

**Prevención:**
- Anota tu contraseña en lugar seguro
- Usa gestor de contraseñas (LastPass, 1Password)

---

## ¿Puedo exportar datos solo de un empleado específico?

**Actualmente:** La exportación incluye todos los empleados.

**Solución temporal:**
- Exporta el archivo CSV completo
- Abre en Excel
- Filtra por el empleado deseado

**Mejora futura:** Se puede agregar filtro en próxima versión.

---

## ¿Los backups son automáticos?

**Sí**, el sistema crea backups automáticamente **cada 10 días**.

**Pero:**
- Sin disco persistente, se pierden al reiniciar el servidor
- **Debes descargarlos manualmente** cada semana para seguridad

---

## ¿Puedo usar este sistema en mi propia empresa?

**Sí**, el sistema es de código abierto.

**Para implementarlo:**
1. Contacta al desarrollador: lemolina0323@gmail.com
2. Se puede personalizar con tu logo y datos
3. Se puede desplegar en tu propio servidor

---

# CONTACTO Y SOPORTE

## Información de Contacto

**Desarrollador:** Luis Molina  
**Email:** lemolina0323@gmail.com  
**GitHub:** https://github.com/TheFaysal24/app_web_empleados

## Tipos de Soporte

### 🆘 Soporte Técnico
- Problemas para acceder al sistema
- Errores en la aplicación
- Restauración de backups
- Configuración avanzada

### 💡 Consultas Generales
- Cómo usar funciones específicas
- Mejoras o nuevas funcionalidades
- Personalización del sistema

### 🐛 Reportar Errores
Al reportar un error, incluye:
- Descripción del problema
- Pasos para reproducirlo
- Capturas de pantalla (si es posible)
- Navegador y dispositivo usado

### 🌟 Sugerencias
Tus ideas son bienvenidas:
- Nuevas funcionalidades
- Mejoras de diseño
- Optimizaciones

## Tiempos de Respuesta

**Email:** 24-48 horas  
**Urgencias:** Indica "URGENTE" en el asunto

---

# GLOSARIO DE TÉRMINOS

**Administrador:** Usuario con permisos completos para gestionar el sistema.

**Backup:** Copia de seguridad de todos los datos del sistema.

**CSV:** Formato de archivo compatible con Excel para exportar datos.

**Dashboard:** Panel principal del sistema con información resumida.

**Deploy:** Proceso de publicar la aplicación en internet.

**Empleado:** Usuario regular con permisos limitados (solo marcar asistencia).

**Horas Extras:** Horas trabajadas adicionales a la jornada normal.

**HTTPS:** Protocolo seguro de comunicación web (candado en navegador).

**Login:** Proceso de iniciar sesión en el sistema.

**Registro:** Entrada de asistencia que incluye inicio, salida y horas.

**Render.com:** Servicio de hosting donde está desplegado el sistema.

**Responsive:** Diseño que se adapta a diferentes tamaños de pantalla.

**URL:** Dirección web del sistema.

---

# ANEXOS

## ANEXO A: Enlaces Rápidos

**Sistema Principal:**
- 🏠 Inicio: https://app-web-empleados.onrender.com
- 🔐 Login: https://app-web-empleados.onrender.com/login
- 📝 Registro: https://app-web-empleados.onrender.com/register

**Panel Administrativo:**
- 📊 Dashboard: https://app-web-empleados.onrender.com/dashboard
- 👥 Gestión Usuarios: https://app-web-empleados.onrender.com/admin/usuarios
- 💾 Backups: https://app-web-empleados.onrender.com/admin/backups
- 📤 Exportar: https://app-web-empleados.onrender.com/exportar_registros

**Configuración:**
- ⚙️ Ajustes: https://app-web-empleados.onrender.com/ajustes

---

## ANEXO B: Atajos de Teclado

**Navegación:**
- `Tab`: Mover entre campos del formulario
- `Enter`: Enviar formulario
- `Esc`: Cerrar modales (ventanas emergentes)

**Navegador:**
- `Ctrl + R` (Win) / `Cmd + R` (Mac): Recargar página
- `Ctrl + T` (Win) / `Cmd + T` (Mac): Nueva pestaña
- `F11`: Pantalla completa

---

## ANEXO C: Capturas de Pantalla Sugeridas

> 📸 **Nota para el PDF:** Toma capturas de pantalla de:

1. **Página de Inicio**
   - Vista completa del gradiente animado
   - Botones principales

2. **Pantalla de Login**
   - Formulario de inicio de sesión
   - Diseño elegante

3. **Pantalla de Registro**
   - Formulario completo
   - Indicador de contraseña

4. **Dashboard Admin**
   - Vista general con estadísticas
   - Gráficos y tablas

5. **Gestión de Usuarios**
   - Tarjetas de usuarios
   - Botones de acciones

6. **Gestión de Backups**
   - Lista de backups
   - Botones de descarga

7. **Dashboard Empleado**
   - Vista simplificada
   - Botones de marcación

8. **Vista Móvil**
   - Captura desde celular
   - Responsive design

---

## ANEXO D: Información Técnica

**Tecnologías Utilizadas:**
- Backend: Python 3 + Flask 2.3.3
- Frontend: HTML5, CSS3, JavaScript
- Hosting: Render.com
- Base de datos: JSON (migrable a SQL)

**Seguridad:**
- Sesiones encriptadas
- HTTPS (SSL/TLS)
- Validación de permisos por rol
- Sistema de bloqueo de usuarios

**Rendimiento:**
- Carga inicial: < 2 segundos
- Responsive en todos los dispositivos
- Compatible con navegadores modernos

---

# NOTAS FINALES

Este manual cubre todas las funcionalidades del Sistema de Gestión de Empleados versión 1.0.

**Última actualización:** Noviembre 2025

Para la versión más reciente de este manual, contacta:
**lemolina0323@gmail.com**

---

## ✅ Checklist de Primeros Pasos

Después de leer este manual:

- [ ] Accede al sistema con las credenciales iniciales
- [ ] Cambia la contraseña del administrador
- [ ] Crea tu primer backup manual
- [ ] Descarga el backup a tu PC
- [ ] Prueba marcar inicio y salida
- [ ] Crea una cuenta de usuario de prueba
- [ ] Exporta datos a CSV
- [ ] Guarda este manual en lugar accesible
- [ ] Comparte la URL con tu equipo

---

**¡Gracias por usar el Sistema de Gestión de Empleados!**

Para soporte, contacta: **lemolina0323@gmail.com**

---

© 2025 Sistema de Gestión de Empleados - Todos los derechos reservados

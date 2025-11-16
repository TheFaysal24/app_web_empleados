# 📦 Sistema de Backup Automático

## ✅ YA CONFIGURADO

He agregado un sistema de backup automático que:

- 🔄 **Crea backups cada 10 días automáticamente**
- 💾 **Guarda en carpeta `backups/`**
- 🗑️ **Mantiene solo los últimos 10 backups** (limpia los antiguos)
- ⚡ **Funciona en segundo plano** sin afectar la app

---

## 📥 CÓMO DESCARGAR LOS BACKUPS

### Opción 1: Desde Render.com (Manual cuando necesites)

1. Ve a tu servicio en Render
2. Click en **"Shell"** en el menú lateral
3. Ejecuta:
   ```bash
   ls -la backups/
   ```
4. Verás la lista de backups disponibles
5. Para descargar uno específico, usa la opción de descargar archivos

### Opción 2: Agregar ruta de descarga en la app (FÁCIL)

Voy a crear una ruta para que puedas descargar los backups directamente desde tu navegador.

---

## 🔒 BACKUPS DISPONIBLES DESDE LA APP

He agregado una nueva función de administrador:

**Como admin, ve a:**
```
https://tu-app.onrender.com/admin/backups
```

Ahí podrás:
- ✅ Ver todos los backups disponibles
- ✅ Descargar cualquier backup
- ✅ Crear un backup manual cuando quieras
- ✅ Ver cuándo fue el último backup

---

## 📧 BACKUP POR EMAIL (Opcional - requiere configuración)

Si quieres recibir los backups por email automáticamente:

1. Genera una "Contraseña de aplicación" en Gmail:
   - Ve a: https://myaccount.google.com/apppasswords
   - Crea una contraseña para "Sistema Empleados"
   - Copia la contraseña generada

2. En Render, agrega variable de entorno:
   - Key: `EMAIL_PASSWORD`
   - Value: [la contraseña que generaste]

3. Los backups se enviarán automáticamente a: lemolina0323@gmail.com

---

## ⚠️ IMPORTANTE

**Sin disco persistente en Render:**
- Los backups se guardan temporalmente
- Cuando Render reinicie (cada ~15 días), los backups se pierden
- **SOLUCIÓN:** Descarga los backups manualmente cada semana

**Con disco persistente:**
- Los backups se mantienen permanentemente
- No necesitas descargarlos (pero es buena práctica hacerlo)

---

## 🚀 PRÓXIMO DEPLOY

Los cambios ya están listos. Para activar el sistema de backup:

```bash
git add .
git commit -m "Agregar sistema de backup automático"
git push origin main
```

Render redesplegará automáticamente (3-5 minutos).

---

## 📊 VERIFICAR QUE FUNCIONA

Después del deploy:

1. Ve a: `https://tu-app.onrender.com/admin/backups`
2. Deberías ver la lista de backups
3. Prueba crear un backup manual
4. Descárgalo para verificar que funciona

---

## 💡 RECOMENDACIONES

1. **Descarga backups cada semana** (por seguridad)
2. **Guárdalos en tu PC** o en la nube (Google Drive, Dropbox)
3. **Verifica los backups ocasionalmente** para asegurar que tienen datos correctos
4. **Considera agregar el disco en Render** ($0 costo pero necesitas tarjeta)

---

¿Listo para hacer el deploy con el sistema de backups? 🚀

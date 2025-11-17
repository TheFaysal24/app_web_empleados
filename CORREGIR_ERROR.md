# 🔧 CORRECCIÓN DE ERROR DE INDENTACIÓN

## ❌ ERROR
```
File "app.py", line 557
    costo_horas_extras = {}
IndentationError: unindent does not match any outer indentation level
```

## ✅ SOLUCIÓN RÁPIDA

### Opción 1: Script Automático (RECOMENDADO)
```bash
python corregir_indentacion.py
```

### Opción 2: Corrección Manual

Abrir `app.py` y en las líneas 556-559, **BORRAR** estas líneas:
```python
       # 🔒 OCULTAR COSTOS PARA USUARIOS NORMALES
       costo_horas_extras = {}  # Vacío para usuarios normales
       costo_total_empresa = 0  # Oculto para usuarios normales
       valor_hora_ordinaria = 0  # Oculto para usuarios normales
```

Y **REEMPLAZAR** con estas (con 8 espacios al inicio):
```python
        # 🔒 OCULTAR COSTOS PARA USUARIOS NORMALES
        costo_horas_extras = {}  # Vacío para usuarios normales
        costo_total_empresa = 0  # Oculto para usuarios normales
        valor_hora_ordinaria = 0  # Oculto para usuarios normales
```

**IMPORTANTE**: Las 4 líneas deben tener **8 espacios** al inicio (igual que la línea anterior `contador_inicios`)

### Opción 3: Revertir Cambios (Si no funciona lo anterior)

Borrar las líneas 556-559 y reemplazar con el código original:
```python
        contador_inicios = {usuario_actual: contador_inicios.get(usuario_actual, 0)}
        costo_horas_extras = {usuario_actual: costo_horas_extras.get(usuario_actual, 0)}
        costo_total_empresa = costo_horas_extras.get(usuario_actual, 0)
        total_usuarios_nuevos = 1  # Solo mostrar 1 para el usuario actual
```

**NOTA**: Esto hace que los usuarios normales vean los costos (no ideal, pero funciona)

---

## ✅ VERIFICAR

Después de corregir, ejecutar:
```bash
python app.py
```

No debe dar error de indentación.

---

## 🎯 RECOMENDACIÓN

**USAR OPCIÓN 1**: Ejecutar el script automático
```bash
python corregir_indentacion.py
```

Esto:
- ✅ Crea backup automático
- ✅ Corrige la indentación
- ✅ Listo para ejecutar

---

**Última alternativa**: Si nada funciona, restaurar desde el backup más reciente:
```bash
# Buscar el backup más reciente
dir /b /o-d app.py.backup.* | more

# Restaurar (reemplaza con el nombre del archivo)
copy app.py.backup.XXXXXXXX_XXXXXX app.py
```

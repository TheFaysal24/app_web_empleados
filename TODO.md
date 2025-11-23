# TODO - Mejoras para admin_gestion_tiempos (resumen uso turnos y gráficos extras)

## Paso 1: Analizar función admin_gestion_tiempos en app.py
- Revisar lógica actual de agregación y armado de estructura de datos `meses`.
- Identificar puntos para agregar nuevos cálculos y variables para la plantilla.

## Paso 2: Agregar resumen uso de turnos por usuario
- Consultar en la base de datos los turnos usados por cada usuario activo en el mes seleccionado.
- Calcular para cada usuario:
  - Cantidad total de turnos usados.
  - Horas extras totales acumuladas.
  - Costo asociado a las horas extras.
- Preparar estructura para renderizar en el nuevo panel "Resumen Uso de Turnos por Usuario".

## Paso 3: Agregar datos para gráficos de horas extras
- Agregar consultas para obtener horas extras diarias agrupadas por usuario.
- Agregar consultas para horas extras semanales y mensuales agregadas.
- Formatear cada conjunto en formato JSON con labels (fechas o semanas) y data (horas).
- Empaquetar en variable `extra_horas` con claves `diario`, `semanal`, `mensual`.

## Paso 4: Modificar llamada a render_template en admin_gestion_tiempos para incluir:
- `resumen_uso` como resumen por usuario.
- `extra_horas` con datos para los 3 gráficos.

## Paso 5: Probar la integración y validar que los datos aparecen correctamente en:
- Nuevo panel debajo del resumen principal.
- Gráficos de barras diarios, semanales y mensuales.

---

# Próximos pasos
- Solicitar confirmación del plan para continuar con la implementación.

# Plan de mejoras para Gestión y Asignación de Turnos con UI Jerárquica y Gráficos

## Objetivo
Desarrollar un sistema completo para:
- Visualizar gestión de tiempos (turnos y registros) por mes, semana, día en UI acordeón.
- Asignar turnos sin sobreescribir, manteniendo registro histórico (bitácora).
- Mostrar resúmenes tabulares y visuales (gráficos) con horas trabajadas y extras.
- Mejorar estética con colores elegantes, botones pequeños y cómodos.
- Permitir usuarios ver sus propios turnos, tiempos y estadísticas gráficas.

## Información Relevante
- Se corrigió bug de cambio de año en gestión de tiempos (semanas 0 ó negativas).
- Actualmente gestión de tiempos con UI acordeón meses-semanas-días ya funciona.
- Nuevo módulo asignar turnos debe tener estructura jerárquica similar con visualización histórica.
- Usuarios necesitan dashboard personal con historial y gráficos.

## Plan de Desarrollo

### 1. Backend
- Modificar/Crear APIs para:
  - Obtener registros históricos sin sobrescribir.
  - Insertar asignaciones sin borrar previas.
  - Agregar datos agregados para resumen de turnos y horas.
- Añadir vistas Flask para:
  - /admin/asignar_turnos con vista jerárquica (mes, semana, día).
  - /usuario/turnos para vista personal del usuario con gráficos.
- Crear modelos o funciones para consultas agregadas (resúmenes por usuario).

### 2. Frontend (Plantillas y Estilos)
- Actualizar Templates:
  - Templates/admin_asignar_turnos.html con acordeón mes-semana-día, tabla resumen y controls para asignar.
  - Templates/usuario_turnos.html con tablas y gráficos (Chart.js o similar).
- Añadir CSS:
  - Botones más pequeños, colores en degradado o pastel, con estilos consistentes !important.
  - Mejorar separación y espacio visual para menos empacado.
- Añadir JS:
  - Funcionalidad acordeón (expandir/colapsar secciones).
  - Scripts para gráficos dinámicos.
  - Funcionalidades para añadir registros sin reemplazar (bitácora).

### 3. Gráficos y Visualización
- Implementar gráficos con librería JS (Chart.js preferida):
  - Horas trabajadas y extras por mes/semanas.
  - Turnos usados vs disponibles.
- Estilizar gráficos con colores armónicos y contrastes suaves.
- Agregar leyendas y tooltips claros.

### 4. UX/UI para Usuarios y Admin
- Interfaces limpias, botones accesibles, tamaños reducidos.
- Navegación intuitiva por períodos temporales.
- Feedback visual para acciones (guardado, error).
- Histórico con posibilidad de filtrar o buscar.

## Archivos a Editar o Crear
- app.py (vistas, lógica backend)
- Templates/admin_asignar_turnos.html (nueva)
- Templates/usuario_turnos.html (nueva)
- Templates/admin_gestion_tiempos.html (posible ajustes)
- static/css/custom_styles.css (u otro para estilos nuevos)
- static/js/turnos.js (scripts nuevos)
- requirements.txt (añadir Chart.js CDN o dependencias frontend)

## Pasos Seguimiento
- Implementar backend APIs y vistas preliminares.
- Crear plantillas HTML con UI acordeón básica.
- Incorporar gráficos estáticos y luego dinámicos.
- Ajustar estilos y comportamiento interactivo.
- Test funcional y visual.
- Documentar instrucciones para usuario y admin.

---

¿Confirmas el plan para proceder con la implementación de estos cambios ampliados y visualmente mejorados?

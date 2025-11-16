# AGENTS.md - app_web_empleados

## Build/Run Commands

- **Start app**: `python app.py` (runs on http://127.0.0.1:5000)
- **Install dependencies**: `pip install -r requirements.txt`
- **No tests configured** - consider adding pytest for testing auth, time tracking, CSV export

## Project Overview

A Flask-based employee time tracking and management application with role-based access (admin/user).

### Architecture

- **Backend**: Flask 2.3.3 with session-based authentication
- **Frontend**: Jinja2 templates (HTML/CSS in `Templates/` directory)
- **Data Storage**: JSON file (`empleados_data.json`) - no database ORM
- **Static Assets**: CSS/JS in `static/` directory

### Key Components

- **Authentication**: Username/password login, session management, admin flag
- **Modules**: Time tracking (inicio/salida), user management, CSV export, password recovery
- **Data Model**: Users, time registrations (date → {inicio, salida, horas_trabajadas, horas_extras}), shifts
- **Admin Features**: Data export (CSV), user management, registration editing

## Code Style

- **Python**: PEP 8 style, Spanish variable/function names (e.g., `cargar_datos`, `marcar_inicio`)
- **No type hints** used
- **Error handling**: Flask flash messages for user feedback
- **Authentication**: Check `'usuario' not in session` before protected routes
- **Data persistence**: Always call `guardar_datos(data)` after modifications
- **Dates**: Use `datetime.date.today().isoformat()` for consistency
- **Hours calculation**: `(end - start).total_seconds() / 3600` for decimal hours

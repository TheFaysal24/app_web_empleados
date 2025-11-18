from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import json
import datetime
import os
import csv
import io
import shutil
import logging
from functools import wraps
import uuid

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Zona horaria y utilidades de tiempo/lock de archivo
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo(os.environ.get('APP_TZ', 'America/Bogota'))
except Exception:
    TZ = None

try:
    import fcntl  # Unix
except Exception:
    fcntl = None
try:
    import msvcrt  # Windows
except Exception:
    msvcrt = None

from contextlib import contextmanager


def now_local():
    """Fecha/hora local consistente. Por defecto America/Bogota, configurable con APP_TZ."""
    try:
        return datetime.datetime.now(TZ) if TZ else datetime.datetime.now()
    except Exception:
        return datetime.datetime.now()


def today_local_iso():
    """Fecha local en ISO (YYYY-MM-DD)."""
    try:
        return now_local().date().isoformat()
    except Exception:
        return datetime.date.today().isoformat()


@contextmanager
def locked_file_write(target_path):
    """Lock de archivo simple entre procesos y escritura atómica (tmp + replace)."""
    lock_path = target_path + '.lock'
    lock_file = open(lock_path, 'w')
    try:
        if msvcrt:
            # Bloqueo en Windows
            try:
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            except Exception:
                pass
        elif fcntl:
            # Bloqueo en Unix
            try:
                fcntl.flock(lock_file, fcntl.LOCK_EX)
            except Exception:
                pass
        yield
    finally:
        try:
            if msvcrt:
                try:
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                except Exception:
                    pass
            elif fcntl:
                try:
                    fcntl.flock(lock_file, fcntl.LOCK_UN)
                except Exception:
                    pass
        finally:
            try:
                lock_file.close()
            except Exception:
                pass
            try:
                os.remove(lock_path)
            except Exception:
                pass

app = Flask(__name__, template_folder='Templates')
app.secret_key = os.environ.get('SECRET_KEY', 'CHANGE_THIS_IN_PRODUCTION_' + os.urandom(24).hex())

# Rate Limiting para proteger contra ataques de fuerza bruta
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://"
)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
login_manager.login_message_category = 'error'

# Protección centralizada de rutas administrativas
@app.before_request
def _proteger_rutas_admin():
    try:
        endpoint = request.endpoint or ''
        if endpoint and endpoint.startswith('admin_'):
            if not current_user.is_authenticated or not getattr(current_user, 'user_data', {}).get('admin', False):
                flash('Acceso denegado', 'error')
                return redirect(url_for('home'))
    except Exception:
        pass

# Clase User para Flask-Login
class User(UserMixin):
    def __init__(self, username, user_data):
        self.id = username
        self.username = username
        self.user_data = user_data

    def is_admin(self):
        return self.user_data.get('admin', False)

    def get_role(self):
        return self.user_data.get('role', 'user')

# Función de backup manual (sin scheduler automático)
def backup_automatico():
    """Crea backup manual del archivo de datos"""
    try:
        fecha = now_local().strftime('%Y%m%d_%H%M%S')
        if not os.path.exists('backups'):
            os.makedirs('backups')

        if os.path.exists(DATA_FILE):
            backup_file = f'backups/empleados_data_backup_{fecha}.json'
            shutil.copy2(DATA_FILE, backup_file)
            print(f"✅ Backup creado: {backup_file}")

            # Limpiar backups antiguos (mantener solo los últimos 10)
            archivos = sorted([f for f in os.listdir('backups') if f.endswith('.json')])
            if len(archivos) > 10:
                for archivo in archivos[:-10]:
                    os.remove(os.path.join('backups', archivo))
            return True
    except Exception as e:
        print(f"❌ Error en backup: {e}")
        return False

DATA_FILE = 'empleados_data.json'

# -------------------
# Flask-Login user loader
# -------------------
@login_manager.user_loader
def load_user(user_id):
    data = cargar_datos()
    if user_id in data['usuarios']:
        return User(user_id, data['usuarios'][user_id])
    return None

# -------------------
# Funciones de carga y guardado
# -------------------
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Asegurar que existan las claves principales
            if 'usuarios' not in data:
                data['usuarios'] = {}
            if 'turnos' not in data:
                data['turnos'] = {}
            if 'registros' not in data:
                data['registros'] = {}
            if 'historial_turnos_mensual' not in data:
                data['historial_turnos_mensual'] = {}
            # Reset tokens storage
            if 'reset_tokens' not in data:
                data['reset_tokens'] = {}
            
            # Asegurar estructura de turnos
            if 'shifts' not in data['turnos']:
                data['turnos']['shifts'] = {
                    'monday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                    'tuesday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                    'wednesday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                    'thursday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                    'friday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                    'saturday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None}
                }
            if 'monthly_assignments' not in data['turnos']:
                data['turnos']['monthly_assignments'] = {}
            if 'current_month' not in data['turnos']:
                data['turnos']['current_month'] = now_local().strftime('%Y-%m')
            
            return data
    
    # Datos iniciales solo si NO existe el archivo
    return {
        'usuarios': {
            'admin': {
                'contrasena': '1234',
                'admin': True,
                'nombre': 'Administrador',
                'cedula': 'N/A',
                'cargo': 'COORDINADOR',
                'correo': 'admin@empresa.com',
                'telefono': ''
            }
        },
        'turnos': {
            'shifts': {
                'monday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'tuesday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'wednesday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'thursday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'friday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'saturday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None}
            },
            'monthly_assignments': {},
            'current_month': now_local().strftime('%Y-%m')
        },
        'registros': {},
        'historial_turnos_mensual': {}
    }

def guardar_datos(data):
    """
    Guarda datos con histórico completo permanente.
    NO sobrescribe datos existentes, solo agrega nuevos.
    """
    # Agregar historial mensual de turnos si no existe
    mes_actual = datetime.datetime.now().strftime('%Y-%m')
    ano_actual = datetime.datetime.now().strftime('%Y')
    
    # Inicializar estructuras de histórico si no existen
    if 'historial_turnos_mensual' not in data:
        data['historial_turnos_mensual'] = {}
    
    if 'historial_registros_diario' not in data:
        data['historial_registros_diario'] = {}
    
    if 'historial_anual' not in data:
        data['historial_anual'] = {}
    
    # Histórico mensual de turnos
    if mes_actual not in data['historial_turnos_mensual']:
        data['historial_turnos_mensual'][mes_actual] = {
            'turnos_asignados': {},
            'registros_asistencia': {},
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    # Guardar snapshot de turnos actuales del mes (NO sobrescribir, solo actualizar)
    if 'turnos' in data and 'monthly_assignments' in data['turnos']:
        # Merge en lugar de reemplazar
        if 'turnos_asignados' not in data['historial_turnos_mensual'][mes_actual]:
            data['historial_turnos_mensual'][mes_actual]['turnos_asignados'] = {}
        
        for usuario, turnos in data['turnos']['monthly_assignments'].items():
            if usuario not in data['historial_turnos_mensual'][mes_actual]['turnos_asignados']:
                data['historial_turnos_mensual'][mes_actual]['turnos_asignados'][usuario] = []
            
            # Agregar solo turnos nuevos
            for turno in turnos:
                if turno not in data['historial_turnos_mensual'][mes_actual]['turnos_asignados'][usuario]:
                    data['historial_turnos_mensual'][mes_actual]['turnos_asignados'][usuario].append(turno)
    
    # Guardar snapshot de registros diarios (histórico permanente)
    for usuario, registros in data.get('registros', {}).items():
        if usuario not in data['historial_registros_diario']:
            data['historial_registros_diario'][usuario] = {}
        
        for fecha, registro in registros.items():
            if isinstance(registro, dict):
                # Guardar copia permanente del registro (NO sobrescribir)
                if fecha not in data['historial_registros_diario'][usuario]:
                    data['historial_registros_diario'][usuario][fecha] = registro.copy()
                    data['historial_registros_diario'][usuario][fecha]['guardado_en'] = datetime.datetime.now().isoformat()
    
    # Histórico anual
    if ano_actual not in data['historial_anual']:
        data['historial_anual'][ano_actual] = {
            'meses': {},
            'timestamp_creacion': datetime.datetime.now().isoformat()
        }
    
    if mes_actual not in data['historial_anual'][ano_actual]['meses']:
        data['historial_anual'][ano_actual]['meses'][mes_actual] = {
            'total_usuarios': len(data.get('usuarios', {})),
            'total_registros': sum(len(regs) for regs in data.get('registros', {}).values()),
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    # Marcar última actualización
    data['ultima_actualizacion'] = now_local().isoformat()

    # Guardar a archivo (escritura atómica con lock)
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    tmp_path = DATA_FILE + '.tmp'
    with locked_file_write(DATA_FILE):
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(json_str)
        os.replace(tmp_path, DATA_FILE)

    logger.info(f"Datos guardados - Usuarios: {len(data.get('usuarios', {}))}, Registros totales: {sum(len(r) for r in data.get('registros', {}).values())}")

# -------------------
# Context processor
# -------------------
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# -------------------
# Rutas principales
# -------------------
@app.route('/')
def home():
    return render_template('home.html')

# ✅ LOGIN con Flask-Login y hash de contraseñas
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")  # Máximo 20 intentos por minuto
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '')
        data = cargar_datos()

        if usuario in data['usuarios']:
            user_data = data['usuarios'][usuario]
            if user_data.get('bloqueado', False):
                logger.warning(f"Intento de login en cuenta bloqueada: {usuario}")
                flash('Tu cuenta está bloqueada. Contacta al administrador.', 'error')
                return redirect(url_for('login'))

            # Verificar contraseña (soporta tanto hash como texto plano para migración)
            password_valid = False
            if user_data['contrasena'].startswith('pbkdf2:sha256:'):
                # Contraseña hasheada
                password_valid = check_password_hash(user_data['contrasena'], contrasena)
            else:
                # Contraseña en texto plano (legacy)
                password_valid = (user_data['contrasena'] == contrasena)
                # Actualizar a hash automáticamente
                if password_valid:
                    user_data['contrasena'] = generate_password_hash(contrasena)
                    guardar_datos(data)
                    logger.info(f"Contraseña migrada a hash para usuario: {usuario}")

            if password_valid:
                user = User(usuario, user_data)
                login_user(user)
                session['usuario'] = usuario
                session['nombre'] = user_data['nombre']
                session['admin'] = user_data.get('admin', False)
                logger.info(f"Login exitoso: {usuario}")
                flash(f'Bienvenido {session["nombre"]}', 'message')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                logger.warning(f"Intento de login fallido para usuario: {usuario}")
        
        flash('Usuario o contraseña incorrectos', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

# Función para asignar turnos automáticamente basado en cédula y rotación
def asignar_turnos_automaticos(data, cedula, usuario):
    """
    Asigna turnos rotativos según el patrón de cada empleado.
    Basado en historial desde Nov 3, 2025.
    
    Patrones de rotación:
    - Natalia (1070963486): 6:30, 8:30 (rotación cada semana)
    - Lesly (1067949514): 8:00, 6:30 (rotación cada semana)
    - Paola (1140870406): 8:30, 9:00 (rotación cada semana)
    - Dayana (1068416077): 9:00, 8:00, 6:30 (rotación cada 3 semanas)
    """
    shift_assignments = {
        "1070963486": ["06:30", "08:30"],
        "1067949514": ["08:00", "06:30"],
        "1140870406": ["08:30", "09:00"],
        "1068416077": ["09:00", "08:00", "06:30"]
    }

    if cedula not in shift_assignments:
        return

    # Calcular qué semana estamos desde Nov 3
    fecha_base = datetime.datetime(2025, 11, 3)
    hoy = datetime.datetime.now()
    semanas_transcurridas = ((hoy - fecha_base).days // 7) + 1
    
    # Obtener patrón de turnos para esta cédula
    patron = shift_assignments[cedula]
    
    # Determinar qué turno le toca esta semana según rotación
    # Semana 1 (Nov 3-8): primer turno del patrón
    # Semana 2 (Nov 10-15): segundo turno del patrón
    # Para Dayana con 3 turnos, rota cada 3 semanas
    indice_turno = (semanas_transcurridas - 1) % len(patron)
    turno_asignado = patron[indice_turno]
    
    # Asignar el turno de esta semana (de lunes a sábado)
    dias_semana = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    
    for dia in dias_semana:
        if turno_asignado in data['turnos']['shifts'][dia]:
            if data['turnos']['shifts'][dia][turno_asignado] is None:
                data['turnos']['shifts'][dia][turno_asignado] = usuario
                
                # Registrar en asignaciones mensuales
                if 'monthly_assignments' not in data['turnos']:
                    data['turnos']['monthly_assignments'] = {}
                if usuario not in data['turnos']['monthly_assignments']:
                    data['turnos']['monthly_assignments'][usuario] = []
                
                turno_key = f"{dia}_{turno_asignado}"
                if turno_key not in data['turnos']['monthly_assignments'][usuario]:
                    data['turnos']['monthly_assignments'][usuario].append(turno_key)

# ✅ Registro - Hash de contraseñas
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")  # Máximo 10 registros por hora
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        cedula = request.form.get('cedula', '').strip()
        cargo = request.form.get('cargo', '').strip()
        correo = request.form.get('correo', '').strip()
        telefono = request.form.get('telefono', '').strip()
        usuario_login = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '')

        # Validaciones básicas
        if not all([nombre, cedula, cargo, correo, usuario_login, contrasena]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('register'))

        if len(contrasena) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('register'))

        data = cargar_datos()
        
        # Buscar si ya existe un usuario con esta cédula
        usuario_existente = None
        for usr, info in data['usuarios'].items():
            if info.get('cedula') == cedula:
                usuario_existente = usr
                break
        
        if usuario_existente:
            # Actualizar información del usuario existente
            data['usuarios'][usuario_existente].update({
                'nombre': nombre,
                'cargo': cargo,
                'correo': correo,
                'telefono': telefono,
                'contrasena': generate_password_hash(contrasena)  # Hash de contraseña
            })
            logger.info(f"Usuario actualizado: {usuario_existente}")
            flash(f'✅ Bienvenido {nombre}! Tu información ha sido actualizada. Usa el usuario: {usuario_existente}', 'message')
            guardar_datos(data)
            return redirect(url_for('login'))
        elif usuario_login not in data['usuarios']:
            # Crear nuevo usuario si no existe
            data['usuarios'][usuario_login] = {
                'nombre': nombre,
                'cedula': cedula,
                'cargo': cargo,
                'correo': correo,
                'telefono': telefono,
                'contrasena': generate_password_hash(contrasena),  # Hash de contraseña
                'admin': False
            }
            asignar_turnos_automaticos(data, cedula, usuario_login)
            guardar_datos(data)
            logger.info(f"Nuevo usuario registrado: {usuario_login}")
            flash('✅ Usuario registrado con éxito. Turnos asignados automáticamente.', 'message')
            return redirect(url_for('login'))
        else:
            flash('El nombre de usuario ya existe.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

# ✅ Logout con Flask-Login
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Sesión cerrada', 'message')
    return redirect(url_for('home'))

# ✅ User Dashboard - Panel personalizado para usuarios regulares
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    admin = session.get('admin', False)

    # Calcular estado de asistencia
    hoy = datetime.date.today().isoformat()
    registros = data['registros'].get(usuario, {})
    attendance_status = 'inactive'
    if hoy in registros and registros[hoy].get('inicio') and not registros[hoy].get('salida'):
        attendance_status = 'active'

    # Preparar datos para el template
    registros_limpios = {}
    for usr, regs in registros.items():
        registros_limpios[usr] = {}
        for key, value in regs.items():
            if isinstance(value, dict) and 'inicio' in value:
                registros_limpios[usr][key] = value

    year = datetime.datetime.now().year

    fechas_horas = {}
    for fecha, reg in registros.items():
        if isinstance(reg, dict):
            fechas_horas[fecha] = reg.get('horas_trabajadas', 0)

    fechas_ordenadas = sorted(fechas_horas.keys())[-7:]
    horas_fechas = [fechas_horas[fecha] for fecha in fechas_ordenadas]

    # Estadísticas básicas para el usuario
    contador_inicios = len(registros)
    costo_horas_extras = 0
    salario_minimo = 1384308
    valor_hora_ordinaria = salario_minimo / (30 * 8)

    for fecha, reg in registros.items():
        if isinstance(reg, dict):
            horas_extras = reg.get('horas_extras', 0)
            try:
                fecha_obj = datetime.datetime.fromisoformat(fecha + 'T00:00:00')
                dia_semana = fecha_obj.weekday()
                if dia_semana >= 5:
                    multiplicador = 1.75 if dia_semana == 5 else 2.0
                else:
                    multiplicador = 1.25
                costo_horas_extras += horas_extras * valor_hora_ordinaria * multiplicador
            except:
                pass

    return render_template('user_dashboard.html',
                         registros=registros_limpios,
                         admin=admin,
                         nombre=session.get('nombre', 'Usuario'),
                         year=year,
                         fechas=fechas_ordenadas,
                         horas_fechas=horas_fechas,
                         attendance_status=attendance_status,
                         contador_inicios=contador_inicios,
                         costo_horas_extras=round(costo_horas_extras, 2),
                         valor_hora_ordinaria=round(valor_hora_ordinaria, 2),
                         session=session)

# ✅ Dashboard - Usuarios normales ven solo su info, admins ven todo
@app.route('/dashboard')
@login_required
def dashboard():
     if 'usuario' not in session:
         flash('Debes iniciar sesión primero', 'error')
         return redirect(url_for('login'))

     data = cargar_datos()
     admin = session.get('admin', False)
     
     # Inicializar acumulados de horas extras para vistas de usuario
     horas_extras_hoy = 0.0
     horas_extras_semana = 0.0
     horas_extras_mes = 0.0
     
     if admin:
         registros = data['registros']
     else:
         usuario_actual = session['usuario']
         registros = {usuario_actual: data['registros'].get(usuario_actual, {})}

     registros_limpios = {}
     for usr, regs in registros.items():
         registros_limpios[usr] = {}
         for key, value in regs.items():
             if isinstance(value, dict) and 'inicio' in value:
                 registros_limpios[usr][key] = value

     year = datetime.datetime.now().year

     fechas_horas = {}
     for usr, info in data['usuarios'].items():
         for fecha, reg in data['registros'].get(usr, {}).items():
             if isinstance(reg, dict):
                 if fecha not in fechas_horas:
                     fechas_horas[fecha] = 0
                 fechas_horas[fecha] += reg.get('horas_trabajadas', 0)

     fechas_ordenadas = sorted(fechas_horas.keys())[-7:]
     horas_fechas = [fechas_horas[fecha] for fecha in fechas_ordenadas]

     # Estadísticas adicionales
     hoy = datetime.date.today().isoformat()
     usuarios_iniciados_hoy = 0
     contador_inicios = {}
     costo_horas_extras = {}

     # Salario mínimo Colombia 2025: $1,384,308
     salario_minimo = 1384308
     valor_hora_ordinaria = salario_minimo / (30 * 8)  # $5,764.61

     for usr, regs in data['registros'].items():
         contador_inicios[usr] = len(regs)
         costo_total = 0

         for fecha, reg in regs.items():
             if isinstance(reg, dict):
                 horas_extras = reg.get('horas_extras', 0)
                 # Determinar multiplicador según día de la semana
                 try:
                     fecha_obj = datetime.datetime.fromisoformat(fecha + 'T00:00:00')
                     dia_semana = fecha_obj.weekday()  # 0=lunes, 4=viernes, 5=sábado, 6=domingo

                     if dia_semana >= 5:  # Sábado o domingo
                         multiplicador = 1.75 if dia_semana == 5 else 2.0
                     else:  # Entre semana
                         multiplicador = 1.25

                     costo_diario = horas_extras * valor_hora_ordinaria * multiplicador
                     costo_total += costo_diario
                 except:
                     pass

         costo_horas_extras[usr] = round(costo_total, 2)

         if hoy in regs and regs[hoy].get('inicio'):
             usuarios_iniciados_hoy += 1

     total_usuarios_nuevos = len(data['usuarios'])
     costo_total_empresa = sum(costo_horas_extras.values())

     # Filtrar datos para usuarios no admin
     if not admin:
         usuario_actual = session['usuario']
         # Filtrar fechas_horas para solo registros del usuario actual
         fechas_horas_filtradas = {}
         for fecha, reg in data['registros'].get(usuario_actual, {}).items():
             if isinstance(reg, dict):
                 fechas_horas_filtradas[fecha] = reg.get('horas_trabajadas', 0)
         fechas_ordenadas = sorted(fechas_horas_filtradas.keys())[-7:]
         horas_fechas = [fechas_horas_filtradas.get(fecha, 0) for fecha in fechas_ordenadas]
         contador_inicios = {usuario_actual: contador_inicios.get(usuario_actual, 0)}

         # Calcular totales de horas extras: diario, semanal y mensual
         registros_usuario = data['registros'].get(usuario_actual, {})
         try:
             hoy_date = datetime.date.today()
             # Diario
             if hoy in registros_usuario and isinstance(registros_usuario[hoy], dict):
                 horas_extras_hoy = float(registros_usuario[hoy].get('horas_extras', 0) or 0)
             # Semanal (lunes a domingo)
             inicio_semana = hoy_date - datetime.timedelta(days=hoy_date.weekday())
             fin_semana = inicio_semana + datetime.timedelta(days=6)
             for f, reg in registros_usuario.items():
                 try:
                     f_date = datetime.date.fromisoformat(f)
                     if inicio_semana <= f_date <= fin_semana and isinstance(reg, dict):
                         horas_extras_semana += float(reg.get('horas_extras', 0) or 0)
                 except:
                     pass
             # Mensual
             for f, reg in registros_usuario.items():
                 try:
                     f_date = datetime.date.fromisoformat(f)
                     if f_date.year == hoy_date.year and f_date.month == hoy_date.month and isinstance(reg, dict):
                         horas_extras_mes += float(reg.get('horas_extras', 0) or 0)
                 except:
                     pass
             horas_extras_hoy = round(horas_extras_hoy, 2)
             horas_extras_semana = round(horas_extras_semana, 2)
             horas_extras_mes = round(horas_extras_mes, 2)
         except Exception:
             pass

         # 🔒 OCULTAR COSTOS PARA USUARIOS NORMALES
         costo_horas_extras = {}  # Vacío para usuarios normales
         costo_total_empresa = 0  # Oculto para usuarios normales
         valor_hora_ordinaria = 0  # Oculto para usuarios normales
         total_usuarios_nuevos = 1  # Solo mostrar 1 para el usuario actual

     # Asegurar que todos los valores sean válidos (nunca None)
     return render_template(
         'dashboard.html',
         registros=registros_limpios or {},
         admin=admin or False,
         nombre=session.get('nombre', 'Usuario'),
         year=year,
         fechas=fechas_ordenadas or [],
         horas_fechas=horas_fechas or [],
         usuarios_iniciados_hoy=usuarios_iniciados_hoy or 0,
         contador_inicios=contador_inicios or {},
         total_usuarios_nuevos=total_usuarios_nuevos or 0,
         costo_horas_extras=costo_horas_extras or {},
         costo_total_empresa=costo_total_empresa or 0,
         valor_hora_ordinaria=round(valor_hora_ordinaria, 2) if valor_hora_ordinaria else 0,
         data=data or {'usuarios': {}, 'turnos': {'shifts': {}, 'monthly_assignments': {}}},
         horas_extras_hoy=horas_extras_hoy,
         horas_extras_semana=horas_extras_semana,
         horas_extras_mes=horas_extras_mes,
         session=session
         )

# ✅ Marcar inicio
@app.route('/marcar_inicio', methods=['POST'])
@login_required
def marcar_inicio():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    hoy = today_local_iso()
    ahora = now_local().isoformat()

    if usuario not in data['registros']:
        data['registros'][usuario] = {}

    if hoy in data['registros'][usuario] and data['registros'][usuario][hoy].get('inicio'):
        flash('Ya registraste tu inicio hoy', 'error')
        return redirect(url_for('dashboard'))

    data['registros'][usuario][hoy] = {
        'inicio': ahora,
        'salida': None,
        'horas_trabajadas': 0,
        'horas_extras': 0
    }

    guardar_datos(data)
    flash('Hora de inicio registrada.', 'message')
    return redirect(url_for('dashboard'))

def calcular_horas(inicio_iso, fin_iso):
    """
    Calcula horas netas (descontando 1h almuerzo) y horas extras (>8h netas).
    Acepta ISO strings o datetime.
    """
    try:
        if isinstance(inicio_iso, datetime.datetime):
            inicio_dt = inicio_iso
        else:
            inicio_dt = datetime.datetime.fromisoformat(inicio_iso)
        if isinstance(fin_iso, datetime.datetime):
            fin_dt = fin_iso
        else:
            fin_dt = datetime.datetime.fromisoformat(fin_iso)
        horas_totales = (fin_dt - inicio_dt).total_seconds() / 3600
        horas_netas = max(0, horas_totales - 1)  # Descuento almuerzo
        horas_extras = max(0, horas_netas - 8)
        return round(horas_netas, 2), round(horas_extras, 2)
    except Exception:
        return 0.0, 0.0

# ✅ Marcar salida
@app.route('/marcar_salida', methods=['POST'])
@login_required
def marcar_salida():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    hoy = today_local_iso()
    ahora = now_local()

    if usuario in data['registros'] and hoy in data['registros'][usuario] and data['registros'][usuario][hoy]['inicio']:
        inicio_iso = data['registros'][usuario][hoy]['inicio']
        horas_trabajadas_netas, horas_extras = calcular_horas(inicio_iso, ahora)
        data['registros'][usuario][hoy]['salida'] = ahora.isoformat()
        data['registros'][usuario][hoy]['horas_trabajadas'] = horas_trabajadas_netas
        data['registros'][usuario][hoy]['horas_extras'] = horas_extras
        guardar_datos(data)

        flash(f'Salida registrada. Horas trabajadas: {horas_trabajadas_netas}h, Extras: {horas_extras}h', 'message')
    else:
        flash('No hay registro de inicio.', 'error')

    return redirect(url_for('dashboard'))

# ✅ Marcar asistencia (Entrada/Salida inteligente)
@app.route('/marcar_asistencia', methods=['POST'])
@login_required
def marcar_asistencia():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    hoy = today_local_iso()
    ahora = now_local()

    # Inicializar registros del usuario si no existen
    if usuario not in data['registros']:
        data['registros'][usuario] = {}

    # Verificar si ya marcó entrada hoy
    if hoy in data['registros'][usuario] and data['registros'][usuario][hoy].get('inicio') and not data['registros'][usuario][hoy].get('salida'):
        # Ya marcó entrada, ahora marcar salida
        inicio_iso = data['registros'][usuario][hoy]['inicio']
        horas_trabajadas_netas, horas_extras = calcular_horas(inicio_iso, ahora)
        data['registros'][usuario][hoy]['salida'] = ahora.isoformat()
        data['registros'][usuario][hoy]['horas_trabajadas'] = horas_trabajadas_netas
        data['registros'][usuario][hoy]['horas_extras'] = horas_extras
        guardar_datos(data)

        flash(f'✅ Salida registrada. Horas trabajadas: {horas_trabajadas_netas}h, Extras: {horas_extras}h', 'message')
    else:
        # No ha marcado entrada hoy, marcar entrada
        if hoy in data['registros'][usuario] and data['registros'][usuario][hoy].get('inicio'):
            flash('Ya registraste tu inicio hoy', 'error')
            return redirect(url_for('dashboard'))

        data['registros'][usuario][hoy] = {
            'inicio': ahora.isoformat(),
            'salida': None,
            'horas_trabajadas': 0,
            'horas_extras': 0
        }
        guardar_datos(data)
        flash('✅ Hora de inicio registrada', 'message')

    return redirect(url_for('dashboard'))

# ✅ Exportar datos
@app.route('/exportar_datos')
def exportar_datos():
     if not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))

     data = cargar_datos()
     output = io.StringIO()
     writer = csv.writer(output)
     
     # Salario mínimo Colombia 2025
     salario_minimo = 1384308
     valor_hora_ordinaria = salario_minimo / (30 * 8)
     
     writer.writerow(['Usuario','Nombre','Cédula','Cargo','Correo','Fecha y Hora Inicio','Fecha y Hora Salida','Horas Trabajadas','Horas Extras','Costo Horas Extras'])

     for usuario, info in data['usuarios'].items():
         registros = data['registros'].get(usuario, {})
         for fecha, reg in registros.items():
             if isinstance(reg, dict):
                 horas_extras = reg.get('horas_extras', 0)
                 
                 # Calcular costo de horas extras
                 try:
                     fecha_obj = datetime.datetime.fromisoformat(fecha + 'T00:00:00')
                     dia_semana = fecha_obj.weekday()
                     
                     if dia_semana >= 5:
                         multiplicador = 1.75 if dia_semana == 5 else 2.0
                     else:
                         multiplicador = 1.25
                     
                     costo = horas_extras * valor_hora_ordinaria * multiplicador
                 except:
                     costo = 0
                 
                 writer.writerow([
                     usuario, info['nombre'], info['cedula'], info['cargo'], info['correo'],
                     reg.get('inicio',''), reg.get('salida',''),
                     reg.get('horas_trabajadas',0), horas_extras, round(costo, 2)
                 ])

     output.seek(0)
     return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                      mimetype='text/csv', as_attachment=True,
                      download_name='datos_empleados.csv')

# ✅ Exportar registros desde dashboard
@app.route('/exportar_registros')
def exportar_registros():
     if not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))

     data = cargar_datos()
     output = io.StringIO()
     writer = csv.writer(output)
     
     # Salario mínimo Colombia 2025
     salario_minimo = 1384308
     valor_hora_ordinaria = salario_minimo / (30 * 8)
     
     writer.writerow(['Usuario','Nombre','Cédula','Cargo','Correo','Fecha y Hora Inicio','Fecha y Hora Salida','Horas Trabajadas','Horas Extras','Costo Horas Extras'])

     for usuario, info in data['usuarios'].items():
         registros = data['registros'].get(usuario, {})
         for fecha, reg in registros.items():
             if isinstance(reg, dict):
                 horas_extras = reg.get('horas_extras', 0)
                 
                 # Calcular costo de horas extras
                 try:
                     fecha_obj = datetime.datetime.fromisoformat(fecha + 'T00:00:00')
                     dia_semana = fecha_obj.weekday()
                     
                     if dia_semana >= 5:
                         multiplicador = 1.75 if dia_semana == 5 else 2.0
                     else:
                         multiplicador = 1.25
                     
                     costo = horas_extras * valor_hora_ordinaria * multiplicador
                 except:
                     costo = 0
                 
                 writer.writerow([
                     usuario, info['nombre'], info['cedula'], info['cargo'], info['correo'],
                     reg.get('inicio',''), reg.get('salida',''),
                     reg.get('horas_trabajadas',0), horas_extras, round(costo, 2)
                 ])

     output.seek(0)
     return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                      mimetype='text/csv', as_attachment=True,
                      download_name='registros_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv')

# ✅ Ajustes de cuenta - Usuarios normales solo pueden cambiar su contraseña
@app.route('/ajustes')
def ajustes():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))
    
    es_admin = session.get('admin', False)
    return render_template('ajustes.html', es_admin=es_admin)

@app.route('/actualizar_datos', methods=['POST'])
def actualizar_datos():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))
    
    if not session.get('admin', False):
        flash('Solo administradores pueden modificar datos personales', 'error')
        return redirect(url_for('ajustes'))

    data = cargar_datos()
    usuario = session['usuario']

    nombre = request.form.get('nombre')
    cargo = request.form.get('cargo')
    correo = request.form.get('correo')
    telefono = request.form.get('telefono')

    if usuario in data['usuarios']:
        if nombre: data['usuarios'][usuario]['nombre'] = nombre
        if cargo: data['usuarios'][usuario]['cargo'] = cargo
        if correo: data['usuarios'][usuario]['correo'] = correo
        if telefono: data['usuarios'][usuario]['telefono'] = telefono
        guardar_datos(data)
        flash('Datos actualizados correctamente', 'message')
    else:
        flash('Usuario no encontrado', 'error')

    return redirect(url_for('ajustes'))

# ✅ Cambiar contraseña con hash
@app.route('/cambiar_contrasena', methods=['POST'])
def cambiar_contrasena():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']

    actual = request.form.get('actual', '')
    nueva = request.form.get('nueva', '')

    if len(nueva) < 6:
        flash('La nueva contraseña debe tener al menos 6 caracteres', 'error')
        return redirect(url_for('ajustes'))

    if usuario in data['usuarios']:
        # Verificar contraseña actual
        password_valid = False
        if data['usuarios'][usuario]['contrasena'].startswith('pbkdf2:sha256:'):
            password_valid = check_password_hash(data['usuarios'][usuario]['contrasena'], actual)
        else:
            password_valid = (data['usuarios'][usuario]['contrasena'] == actual)
        
        if password_valid:
            data['usuarios'][usuario]['contrasena'] = generate_password_hash(nueva)
            guardar_datos(data)
            logger.info(f"Contraseña cambiada para usuario: {usuario}")
            flash('Contraseña actualizada correctamente', 'message')
        else:
            flash('La contraseña actual no es correcta', 'error')
    else:
        flash('Usuario no encontrado', 'error')

    return redirect(url_for('ajustes'))

# ✅ Recuperar contraseña (genera nueva contraseña y envía notificación)
@app.route('/recuperar_contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        data = cargar_datos()
        for usr, info in data.get('usuarios', {}).items():
            if info.get('correo') == correo:
                # Generar token temporal con expiración (60 minutos)
                token = uuid.uuid4().hex
                expira = (now_local() + datetime.timedelta(minutes=60)).isoformat()
                if 'reset_tokens' not in data:
                    data['reset_tokens'] = {}
                data['reset_tokens'][token] = {
                    'usuario': usr,
                    'expira': expira
                }
                guardar_datos(data)

                # Construir enlace de restablecimiento absoluto
                base_url = request.url_root.rstrip('/')
                reset_url = f"{base_url}{url_for('reset_password')}?token={token}"

                # Preparar mailto con el enlace
                import urllib.parse
                asunto = urllib.parse.quote("Restablecimiento de Contraseña - Sistema Empleados")
                cuerpo = urllib.parse.quote(
                    f"Hola {info.get('nombre', usr)},\n\n"
                    f"Hemos recibido tu solicitud para restablecer la contraseña.\n"
                    f"Por favor, haz clic en el siguiente enlace (válido por 60 minutos):\n{reset_url}\n\n"
                    f"Si no solicitaste este cambio, ignora este mensaje.\n\n"
                    f"Saludos,\nSistema de Empleados"
                )
                mailto_link = f"mailto:{correo}?subject={asunto}&body={cuerpo}"

                flash(
                    f'✅ Hemos generado un enlace de restablecimiento. '
                    f'<a href="{mailto_link}" target="_blank" style="color:#fff;text-decoration:underline;">📧 Enviar al correo</a>',
                    'message'
                )
                return redirect(url_for('login'))
        flash('Correo no encontrado', 'error')
        return redirect(url_for('recuperar_contrasena'))
    return render_template('recuperar_contrasena.html')

# ✅ Panel de Administración
@app.route('/admin/usuarios')
def admin_usuarios():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     data = cargar_datos()
     usuarios = data['usuarios']
     registros = data['registros']
     
     return render_template('admin_usuarios.html', usuarios=usuarios, registros=registros)

# ✅ Cambiar contraseña de usuario (Admin)
@app.route('/admin/cambiar_clave', methods=['GET', 'POST'])
def admin_cambiar_clave():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     data = cargar_datos()
     
     if request.method == 'POST':
         usuario = request.form.get('usuario')
         nueva_clave = request.form.get('nueva_clave')
         
         if usuario in data['usuarios'] and nueva_clave:
             data['usuarios'][usuario]['contrasena'] = generate_password_hash(nueva_clave)
             guardar_datos(data)
             flash(f'Contraseña actualizada para {usuario}', 'message')
         else:
             flash('Error al actualizar contraseña', 'error')
         
         return redirect(url_for('admin_usuarios'))
     
     usuario = request.args.get('usuario')
     if usuario and usuario in data['usuarios']:
         return render_template('admin_cambiar_clave.html', usuario=usuario, datos=data['usuarios'][usuario])
     
     flash('Usuario no encontrado', 'error')
     return redirect(url_for('admin_usuarios'))

# ✅ Desbloquear usuario (Admin)
@app.route('/admin/desbloquear', methods=['POST'])
def admin_desbloquear():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     usuario = request.form.get('usuario')
     data = cargar_datos()
     
     if usuario and usuario in data['usuarios']:
         data['usuarios'][usuario]['bloqueado'] = False
         guardar_datos(data)
         flash(f'Usuario {usuario} desbloqueado', 'message')
     else:
         flash('Usuario no encontrado', 'error')
     
     return redirect(url_for('admin_usuarios'))

# ✅ Bloquear usuario (Admin)
@app.route('/admin/bloquear', methods=['POST'])
def admin_bloquear():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     usuario = request.form.get('usuario')
     data = cargar_datos()
     
     if usuario and usuario in data['usuarios']:
         data['usuarios'][usuario]['bloqueado'] = True
         guardar_datos(data)
         flash(f'Usuario {usuario} bloqueado', 'message')
     else:
         flash('Usuario no encontrado', 'error')
     
     return redirect(url_for('admin_usuarios'))

# ✅ Eliminar registro (Admin)
@app.route('/admin/eliminar_registro', methods=['POST'])
def admin_eliminar_registro():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('dashboard'))
     
     usuario = request.form.get('usuario')
     fecha = request.form.get('fecha')
     data = cargar_datos()
     
     if usuario and fecha and usuario in data['registros'] and fecha in data['registros'][usuario]:
         del data['registros'][usuario][fecha]
         guardar_datos(data)
         flash(f'Registro del {fecha} eliminado para {usuario}', 'message')
     else:
         flash('Registro no encontrado', 'error')
     
     return redirect(url_for('admin_usuarios'))



# ✅ Editar registro (Admin)
@app.route('/admin/editar_registro', methods=['GET', 'POST'])
def admin_editar_registro():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('dashboard'))
     
     data = cargar_datos()
     
     if request.method == 'POST':
         usuario = request.form.get('usuario')
         fecha = request.form.get('fecha')
         inicio = request.form.get('inicio')
         salida = request.form.get('salida')
         
         if usuario and fecha and usuario in data['registros'] and fecha in data['registros'][usuario]:
             data['registros'][usuario][fecha]['inicio'] = inicio
             data['registros'][usuario][fecha]['salida'] = salida
             
             if inicio and salida:
                 horas_trabajadas, horas_extras = calcular_horas(inicio, salida)
                 
                 data['registros'][usuario][fecha]['horas_trabajadas'] = horas_trabajadas
                 data['registros'][usuario][fecha]['horas_extras'] = horas_extras
             
             guardar_datos(data)
             flash('Registro actualizado correctamente', 'message')
             return redirect(url_for('admin_usuarios'))
     
     usuario = request.args.get('usuario')
     fecha = request.args.get('fecha')
     
     if usuario and fecha and usuario in data['registros'] and fecha in data['registros'][usuario]:
         registro = data['registros'][usuario][fecha]
         return render_template('editar_registro.html', usuario=usuario, fecha=fecha, registro=registro)
     
     flash('Registro no encontrado', 'error')
     return redirect(url_for('admin_usuarios'))

# ✅ Gestión de Backups (Admin)
@app.route('/admin/backups')
def admin_backups():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     backups_list = []
     if os.path.exists('backups'):
         archivos = sorted([f for f in os.listdir('backups') if f.endswith('.json')], reverse=True)
         for archivo in archivos:
             ruta = os.path.join('backups', archivo)
             tamaño = os.path.getsize(ruta)
             fecha_mod = datetime.datetime.fromtimestamp(os.path.getmtime(ruta))
             backups_list.append({
                 'nombre': archivo,
                 'tamaño': round(tamaño / 1024, 2),  # KB
                 'fecha': fecha_mod.strftime('%d/%m/%Y %H:%M:%S')
             })
     
     return render_template('admin_backups.html', backups=backups_list)

@app.route('/admin/crear_backup')
def admin_crear_backup():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     backup_automatico()
     flash('Backup creado exitosamente', 'message')
     return redirect(url_for('admin_backups'))

@app.route('/admin/descargar_backup/<nombre>')
def admin_descargar_backup(nombre):
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     ruta = os.path.join('backups', nombre)
     if os.path.exists(ruta):
         return send_file(ruta, as_attachment=True, download_name=nombre)
     else:
         flash('Backup no encontrado', 'error')
         return redirect(url_for('admin_backups'))

# ✅ Seleccionar turno semanal
@app.route('/seleccionar_turno', methods=['GET', 'POST'])
def seleccionar_turno():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    cedula = data['usuarios'][usuario].get('cedula', '')

    if request.method == 'POST':
        turno = request.form.get('turno')  # Formato: "dia_hora"

        if not turno:
            flash('Selecciona un turno válido', 'error')
            return redirect(url_for('seleccionar_turno'))

        dia, hora = turno.split('_')

        # Validar que el turno esté disponible
        if data['turnos']['shifts'][dia][hora] is not None:
            flash('Este turno ya está ocupado', 'error')
            return redirect(url_for('seleccionar_turno'))

        # Asignar turno
        data['turnos']['shifts'][dia][hora] = usuario

        # Registrar asignación mensual
        if 'monthly_assignments' not in data['turnos']:
            data['turnos']['monthly_assignments'] = {}
        if usuario not in data['turnos']['monthly_assignments']:
            data['turnos']['monthly_assignments'][usuario] = []
        data['turnos']['monthly_assignments'][usuario].append(f"{dia}_{hora}")

        guardar_datos(data)
        flash('✅ Turno seleccionado exitosamente', 'message')
        return redirect(url_for('ver_turnos_asignados'))

    # TODOS los turnos disponibles para TODOS los gestores
    turnos_permitidos = ["06:30", "08:00", "08:30", "09:00"]

    # Obtener turnos ya usados por este usuario en el historial (opcional, no restringe)
    turnos_usados_usuario = {}
    if 'historial_semanal' in data['turnos']:
        for semana, info_semana in data['turnos']['historial_semanal'].items():
            if usuario in info_semana.get('asignaciones', {}):
                for asignacion in info_semana['asignaciones'][usuario]:
                    dia = asignacion['dia_semana']
                    hora = asignacion['hora']
                    # Mapear nombre de día a clave
                    dia_map = {'lunes': 'monday', 'martes': 'tuesday', 'miercoles': 'wednesday',
                              'jueves': 'thursday', 'viernes': 'friday', 'sabado': 'saturday'}
                    dia_key = dia_map.get(dia, dia)
                    if dia_key not in turnos_usados_usuario:
                        turnos_usados_usuario[dia_key] = []
                    turnos_usados_usuario[dia_key].append(hora)

    # Preparar datos para el template - TODOS los turnos disponibles si no están ocupados por OTRO usuario
    shifts = data['turnos']['shifts']
    available_shifts = {}

    for dia, horas in shifts.items():
        available_shifts[dia] = {}
        for hora, assigned_user in horas.items():
            # Verificar: 1) está en su patrón, 2) no ocupado por OTRO usuario
            esta_en_patron = hora in turnos_permitidos
            no_ocupado_por_otro = assigned_user is None or assigned_user == usuario
            
            # Disponible si está en su patrón y no lo tiene otro usuario
            available_shifts[dia][hora] = esta_en_patron and no_ocupado_por_otro

    return render_template('seleccionar_turno.html',
                         shifts=shifts,
                         available_shifts=available_shifts,
                         turnos_usados_usuario=turnos_usados_usuario,
                         session=session)

# ✅ Ver turnos asignados
@app.route('/ver_turnos_asignados')
def ver_turnos_asignados():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    admin = session.get('admin', False)
    
    # Inicializar assigned_shifts
    assigned_shifts = {}

    if admin:
        # Mostrar todos los turnos asignados con datos completos
        if 'turnos' in data and 'shifts' in data['turnos']:
            for dia, horas in data['turnos']['shifts'].items():
                if horas and isinstance(horas, dict):
                    for hora, assigned_user in horas.items():
                        if assigned_user and assigned_user in data.get('usuarios', {}):
                            if assigned_user not in assigned_shifts:
                                assigned_shifts[assigned_user] = []
                            user_data = data['usuarios'].get(assigned_user, {})
                            assigned_shifts[assigned_user].append({
                                'dia': dia,
                                'hora': hora,
                                'usuario': assigned_user,
                                'nombre': user_data.get('nombre', assigned_user),
                                'cedula': user_data.get('cedula', 'N/A'),
                                'cargo': user_data.get('cargo', 'Gestor Operativo')
                            })
    else:
        # Mostrar solo turnos del usuario actual
        assigned_shifts[usuario] = []
        if 'turnos' in data and 'shifts' in data['turnos']:
            for dia, horas in data['turnos']['shifts'].items():
                if horas and isinstance(horas, dict):
                    for hora, assigned_user in horas.items():
                        if assigned_user == usuario and usuario in data.get('usuarios', {}):
                            user_data = data['usuarios'][usuario]
                            assigned_shifts[usuario].append({
                                'dia': dia,
                                'hora': hora,
                                'usuario': usuario,
                                'nombre': user_data.get('nombre', usuario),
                                'cedula': user_data.get('cedula', 'N/A'),
                                'cargo': user_data.get('cargo', 'Gestor Operativo')
                            })

    # Asegurar que nunca pasemos None
    if not assigned_shifts:
        assigned_shifts = {}
    if not data:
        data = {'usuarios': {}, 'turnos': {'shifts': {}}}
    
    return render_template('ver_turnos_asignados.html',
                         assigned_shifts=assigned_shifts,
                         admin=admin,
                         data=data,
                         session=session)

# ✅ Eliminar turno
@app.route('/eliminar_turno', methods=['POST'])
def eliminar_turno():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    dia = request.form.get('dia')
    hora = request.form.get('hora')

    if not dia or not hora:
        flash('Datos de turno inválidos', 'error')
        return redirect(url_for('ver_turnos_asignados'))

    # Verificar que el turno pertenece al usuario o es admin
    turno_usuario = data.get('turnos', {}).get('shifts', {}).get(dia, {}).get(hora)
    
    if turno_usuario == usuario or session.get('admin'):
        # Liberar el turno
        if dia in data['turnos']['shifts'] and hora in data['turnos']['shifts'][dia]:
            data['turnos']['shifts'][dia][hora] = None
            
            # Remover de asignaciones mensuales
            turno_key = f"{dia}_{hora}"
            if 'monthly_assignments' in data['turnos']:
                # Remover del usuario que lo tenía asignado
                usuario_a_limpiar = turno_usuario if session.get('admin') else usuario
                if usuario_a_limpiar in data['turnos']['monthly_assignments']:
                    if turno_key in data['turnos']['monthly_assignments'][usuario_a_limpiar]:
                        data['turnos']['monthly_assignments'][usuario_a_limpiar].remove(turno_key)
            
            guardar_datos(data)
            flash('✅ Turno eliminado correctamente y disponible para otros', 'message')
    else:
        flash('No puedes eliminar este turno', 'error')

    return redirect(url_for('ver_turnos_asignados'))

# ✅ Panel de asignación manual de turnos (Admin)
@app.route('/admin/asignar_turnos')
def admin_asignar_turnos():
    if 'usuario' not in session or not session.get('admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    data = cargar_datos()
    
    # Obtener solo gestores (usuarios con cédula en el sistema de turnos)
    cedulas_gestores = ["1070963486", "1067949514", "1140870406", "1068416077"]
    gestores = {}
    
    for usr, info in data.get('usuarios', {}).items():
        if info.get('cedula') in cedulas_gestores:
            gestores[usr] = {
                'nombre': info.get('nombre', usr),
                'cedula': info.get('cedula', 'N/A'),
                'cargo': info.get('cargo', 'Gestor Operativo')
            }
    
    return render_template('admin_asignar_turnos.html',
                         shifts=data.get('turnos', {}).get('shifts', {}),
                         gestores=gestores,
                         data=data)

# ✅ Asignar turno manual (Admin)
@app.route('/admin/asignar_turno_manual', methods=['POST'])
def admin_asignar_turno_manual():
    if 'usuario' not in session or not session.get('admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    data = cargar_datos()
    dia = request.form.get('dia')
    hora = request.form.get('hora')
    usuario = request.form.get('usuario')
    
    if dia and hora:
        if usuario:
            # Asignar turno al usuario
            data['turnos']['shifts'][dia][hora] = usuario
            
            # Actualizar asignaciones mensuales
            if 'monthly_assignments' not in data['turnos']:
                data['turnos']['monthly_assignments'] = {}
            if usuario not in data['turnos']['monthly_assignments']:
                data['turnos']['monthly_assignments'][usuario] = []
            
            turno_key = f"{dia}_{hora}"
            if turno_key not in data['turnos']['monthly_assignments'][usuario]:
                data['turnos']['monthly_assignments'][usuario].append(turno_key)
            
            flash(f'✅ Turno asignado a {data["usuarios"][usuario]["nombre"]}', 'message')
        else:
            # Limpiar el turno
            usuario_anterior = data['turnos']['shifts'][dia][hora]
            data['turnos']['shifts'][dia][hora] = None
            
            # Remover de asignaciones
            if usuario_anterior and 'monthly_assignments' in data['turnos']:
                if usuario_anterior in data['turnos']['monthly_assignments']:
                    turno_key = f"{dia}_{hora}"
                    if turno_key in data['turnos']['monthly_assignments'][usuario_anterior]:
                        data['turnos']['monthly_assignments'][usuario_anterior].remove(turno_key)
            
            flash('✅ Turno liberado', 'message')
        
        guardar_datos(data)
    
    return redirect(url_for('admin_asignar_turnos'))

# ✅ Limpiar turno (Admin)
@app.route('/admin/limpiar_turno', methods=['POST'])
def admin_limpiar_turno():
    if 'usuario' not in session or not session.get('admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    data = cargar_datos()
    dia = request.form.get('dia')
    hora = request.form.get('hora')
    
    if dia and hora and dia in data['turnos']['shifts']:
        usuario_anterior = data['turnos']['shifts'][dia][hora]
        data['turnos']['shifts'][dia][hora] = None
        
        # Remover de asignaciones mensuales
        if usuario_anterior and 'monthly_assignments' in data['turnos']:
            if usuario_anterior in data['turnos']['monthly_assignments']:
                turno_key = f"{dia}_{hora}"
                if turno_key in data['turnos']['monthly_assignments'][usuario_anterior]:
                    data['turnos']['monthly_assignments'][usuario_anterior].remove(turno_key)
        
        guardar_datos(data)
        flash('✅ Turno liberado', 'message')
    
    return redirect(url_for('admin_asignar_turnos'))

# ✅ Panel de edición completa de usuario (Admin)
@app.route('/admin/editar_completo/<usuario>')
def admin_editar_completo(usuario):
    if 'usuario' not in session or not session.get('admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    data = cargar_datos()
    
    if usuario not in data.get('usuarios', {}):
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin_usuarios'))
    
    usuario_data = data['usuarios'][usuario]
    registros = data.get('registros', {}).get(usuario, {})
    
    return render_template('admin_editar_completo.html',
                         usuario=usuario,
                         usuario_data=usuario_data,
                         registros=registros)

# ✅ Actualizar usuario completo (Admin)
@app.route('/admin/actualizar_usuario_completo', methods=['POST'])
def admin_actualizar_usuario_completo():
    if 'usuario' not in session or not session.get('admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    data = cargar_datos()
    usuario = request.form.get('usuario')
    
    if usuario in data['usuarios']:
        data['usuarios'][usuario]['nombre'] = request.form.get('nombre')
        data['usuarios'][usuario]['cedula'] = request.form.get('cedula')
        data['usuarios'][usuario]['cargo'] = request.form.get('cargo')
        data['usuarios'][usuario]['correo'] = request.form.get('correo')
        data['usuarios'][usuario]['telefono'] = request.form.get('telefono', '')
        data['usuarios'][usuario]['admin'] = request.form.get('admin') == 'true'
        
        # Cambiar contraseña si se proporcionó
        nueva_contrasena = request.form.get('contrasena')
        if nueva_contrasena:
            data['usuarios'][usuario]['contrasena'] = generate_password_hash(nueva_contrasena)
        
        guardar_datos(data)
        flash('✅ Usuario actualizado completamente', 'message')
    
    return redirect(url_for('admin_usuarios'))

# ✅ Actualizar registro de asistencia (Admin - AJAX)
@app.route('/admin/actualizar_registro', methods=['POST'])
def admin_actualizar_registro():
    if 'usuario' not in session or not session.get('admin'):
        return jsonify({'success': False, 'error': 'Acceso denegado'}), 403
    
    data = cargar_datos()
    usuario = request.form.get('usuario')
    fecha = request.form.get('fecha')
    inicio = request.form.get('inicio')
    salida = request.form.get('salida')
    
    if usuario in data.get('registros', {}) and fecha in data['registros'][usuario]:
        try:
            data['registros'][usuario][fecha]['inicio'] = inicio
            data['registros'][usuario][fecha]['salida'] = salida
            
            # Recalcular horas
            if inicio and salida:
                horas_netas, horas_extras = calcular_horas(inicio, salida)
                
                data['registros'][usuario][fecha]['horas_trabajadas'] = horas_netas
                data['registros'][usuario][fecha]['horas_extras'] = horas_extras
            
            guardar_datos(data)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    return jsonify({'success': False, 'error': 'Registro no encontrado'}), 404

# ✅ Eliminar usuario (Admin)
@app.route('/admin/eliminar_usuario/<usuario>')
def admin_eliminar_usuario(usuario):
    if 'usuario' not in session or not session.get('admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    data = cargar_datos()
    
    if usuario in data['usuarios']:
        # No permitir eliminar el propio usuario admin
        if usuario == session['usuario']:
            flash('No puedes eliminar tu propio usuario', 'error')
            return redirect(url_for('admin_usuarios'))
        
        # Eliminar usuario
        del data['usuarios'][usuario]
        
        # Limpiar sus registros
        if usuario in data.get('registros', {}):
            del data['registros'][usuario]
        
        # Limpiar sus turnos
        if 'turnos' in data:
            for dia in data['turnos'].get('shifts', {}).values():
                for hora in list(dia.keys()):
                    if dia[hora] == usuario:
                        dia[hora] = None
            
            if usuario in data['turnos'].get('monthly_assignments', {}):
                del data['turnos']['monthly_assignments'][usuario]
        
        guardar_datos(data)
        flash(f'✅ Usuario {usuario} eliminado completamente', 'message')
    
    return redirect(url_for('admin_usuarios'))

# Función auxiliar para validar selección de turno
def validar_turno_usuario(data, usuario, user_role, dia, hora):
    current_month = data['turnos']['current_month']
    monthly_assignments = data['turnos']['monthly_assignments'].get(usuario, [])

    # Contar turnos asignados este mes
    turnos_mes = len(monthly_assignments)

    # Si ya tiene 4 turnos, no puede seleccionar más hasta próximo mes
    if turnos_mes >= 4:
        return False

    # Verificar que no se repita el turno en el mes
    turno_key = f"{dia}_{hora}"
    if turno_key in monthly_assignments:
        return False

    # Managers pueden seleccionar cualquier turno disponible
    if user_role == 'manager':
        return True

    # Collaborators tienen restricciones
    # Solo pueden seleccionar turnos de 8:00 en adelante los días de semana
    if dia in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        if hora in ['06:30', '08:00']:
            return False

    return True

# ✅ Módulo de Turnos con Trazabilidad
@app.route('/modulo_turnos')
def modulo_turnos():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))
    
    data = cargar_datos()
    semana_param = request.args.get('semana', type=int)
    
    # Fecha de inicio: 3 de noviembre de 2025
    fecha_base = datetime.datetime(2025, 11, 3)
    hoy = datetime.datetime.now()
    
    # Calcular semana actual desde Nov 3
    dias_transcurridos = (hoy - fecha_base).days
    semana_actual = (dias_transcurridos // 7) + 1
    
    # Si se especifica semana en parámetro, usarla
    if semana_param:
        semana_actual = semana_param
    
    # Calcular fechas de la semana
    inicio_semana = fecha_base + datetime.timedelta(weeks=semana_actual-1)
    fin_semana = inicio_semana + datetime.timedelta(days=5)
    
    fechas_semana = []
    for i in range(6):  # Lunes a Sábado
        fecha = inicio_semana + datetime.timedelta(days=i)
        fechas_semana.append(fecha.strftime('%d/%m/%Y'))
    
    # Historial de turnos desde Nov 3, 2025
    historial_turnos = generar_historial_turnos(data, fecha_base)
    
    # Estadísticas
    total_turnos = sum(1 for dia in data['turnos']['shifts'].values() for usr in dia.values() if usr)
    usuarios_activos = len(set(usr for dia in data['turnos']['shifts'].values() for usr in dia.values() if usr))
    turnos_libres = sum(1 for dia in data['turnos']['shifts'].values() for usr in dia.values() if not usr)
    
    stats = {
        'total_turnos': total_turnos,
        'usuarios_activos': usuarios_activos,
        'turnos_libres': turnos_libres
    }
    
    # Información de usuarios con turnos
    usuarios_turnos = obtener_usuarios_con_turnos(data)
    
    return render_template('modulo_turnos.html',
                         semana_actual=semana_actual,
                         fecha_inicio_semana=inicio_semana.strftime('%d/%m/%Y'),
                         fecha_fin_semana=fin_semana.strftime('%d/%m/%Y'),
                         fechas_semana=fechas_semana,
                         turnos_semana=data['turnos']['shifts'],
                         historial_turnos=historial_turnos,
                         usuarios_turnos=usuarios_turnos,
                         stats=stats,
                         data=data)

def generar_historial_turnos(data, fecha_base):
    """Genera historial completo de turnos desde Nov 3, 2025"""
    historial = []
    
    # Configuración de turnos por cédula
    asignaciones_base = {
        "1070963486": {
            "usuario": None,
            "turnos": ["06:30", "08:30"],
            "cedula": "1070963486"
        },
        "1067949514": {
            "usuario": None,
            "turnos": ["08:00", "06:30"],
            "cedula": "1067949514"
        },
        "1140870406": {
            "usuario": None,
            "turnos": ["08:30", "09:00"],
            "cedula": "1140870406"
        },
        "1068416077": {
            "usuario": None,
            "turnos": ["09:00", "08:00", "06:30"],  # Empezando con 6:30 esta semana
            "cedula": "1068416077"
        }
    }
    
    # Encontrar usuarios por cédula
    for usuario, info in data['usuarios'].items():
        cedula = info.get('cedula', '')
        if cedula in asignaciones_base:
            asignaciones_base[cedula]['usuario'] = usuario
            asignaciones_base[cedula]['nombre'] = info.get('nombre', usuario)
            asignaciones_base[cedula]['cargo'] = info.get('cargo', 'N/A')
    
    # Generar historial semanal desde Nov 3
    hoy = datetime.datetime.now()
    semanas_transcurridas = ((hoy - fecha_base).days // 7) + 1
    
    for semana in range(1, semanas_transcurridas + 1):
        fecha_inicio = fecha_base + datetime.timedelta(weeks=semana-1)
        
        for cedula, info in asignaciones_base.items():
            if info['usuario']:
                # Determinar estado
                if semana < semanas_transcurridas:
                    estado = "Completado"
                    estado_class = "success"
                elif semana == semanas_transcurridas:
                    estado = "En Curso"
                    estado_class = "warning"
                else:
                    estado = "Pendiente"
                    estado_class = "info"
                
                historial.append({
                    'semana': semana,
                    'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                    'usuario': info['nombre'],
                    'cedula': cedula,
                    'cargo': info['cargo'],
                    'turnos': info['turnos'],
                    'estado': estado,
                    'estado_class': estado_class
                })
    
    return sorted(historial, key=lambda x: x['semana'], reverse=True)

def obtener_usuarios_con_turnos(data):
    """Obtiene información de usuarios con sus patrones de turnos"""
    usuarios_info = []
    
    patrones_cedula = {
        "1070963486": ["06:30", "08:30"],
        "1067949514": ["08:00", "06:30"],
        "1140870406": ["08:30", "09:00"],
        "1068416077": ["09:00", "08:00", "06:30"]
    }
    
    for usuario, info in data.get('usuarios', {}).items():
        cedula = info.get('cedula', '')
        if cedula in patrones_cedula:
            # Contar turnos del usuario
            total_turnos = 0
            if 'turnos' in data and 'shifts' in data['turnos']:
                total_turnos = sum(1 for dia in data['turnos']['shifts'].values() 
                                 for usr in dia.values() if usr == usuario)
            
            usuarios_info.append({
                'usuario': usuario,
                'nombre': info.get('nombre', usuario),
                'cedula': cedula,
                'cargo': info.get('cargo', 'N/A'),
                'total_turnos': total_turnos,
                'patron': patrones_cedula[cedula]
            })
    
    return usuarios_info

# ✅ NUEVO: Módulo de Turnos Mensual Mejorado
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.values.get('token', '').strip()
    data = cargar_datos()

    # Validar token
    info_token = data.get('reset_tokens', {}).get(token)
    if not token or not info_token:
        flash('Token inválido o expirado', 'error')
        return redirect(url_for('recuperar_contrasena'))

    # Comprobar expiración
    try:
        expira_dt = datetime.datetime.fromisoformat(info_token.get('expira'))
        if now_local() > expira_dt:
            # Borrar token expirado
            del data['reset_tokens'][token]
            guardar_datos(data)
            flash('El token ha expirado. Solicita uno nuevo.', 'error')
            return redirect(url_for('recuperar_contrasena'))
    except Exception:
        flash('Token inválido', 'error')
        return redirect(url_for('recuperar_contrasena'))

    if request.method == 'POST':
        nueva = request.form.get('nueva', '')
        confirmar = request.form.get('confirmar', '')
        if len(nueva) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres', 'error')
            return redirect(url_for('reset_password', token=token))
        if nueva != confirmar:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('reset_password', token=token))

        usuario = info_token.get('usuario')
        if usuario in data.get('usuarios', {}):
            data['usuarios'][usuario]['contrasena'] = generate_password_hash(nueva)
            # Invalidar token
            if token in data.get('reset_tokens', {}):
                del data['reset_tokens'][token]
            guardar_datos(data)
            flash('✅ Contraseña restablecida correctamente. Ya puedes iniciar sesión.', 'message')
            return redirect(url_for('login'))
        else:
            flash('Usuario no encontrado para el token', 'error')
            return redirect(url_for('recuperar_contrasena'))

    # GET: mostrar formulario
    return render_template('reset_password.html', token=token)

@app.route('/turnos_mensual')
@login_required
def turnos_mensual():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))
    
    data = cargar_datos()
    
    # Obtener mes y año de parámetros o usar actual
    mes = request.args.get('mes', type=int) or now_local().month
    ano = request.args.get('ano', type=int) or now_local().year
    
    # Nombres de meses
    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    # Patrones de turnos por cédula
    patrones_cedula = {
        "1070963486": ["06:30", "08:30"],
        "1067949514": ["08:00", "06:30"],
        "1140870406": ["08:30", "09:00"],
        "1068416077": ["09:00", "08:00", "06:30"]
    }
    
    # Límite mensual de turnos por gestor (ej: 20 turnos máximo al mes)
    LIMITE_MENSUAL_TURNOS = 20
    
    # Procesar datos de gestores
    gestores_data = []
    for usuario, info in data.get('usuarios', {}).items():
        cedula = info.get('cedula', '')
        if cedula in patrones_cedula:
            # Obtener turnos usados este mes
            turnos_usados_mes = []
            if 'registros' in data and usuario in data['registros']:
                for fecha, reg in data['registros'][usuario].items():
                    try:
                        fecha_obj = datetime.datetime.fromisoformat(fecha)
                        if fecha_obj.month == mes and fecha_obj.year == ano:
                            if isinstance(reg, dict) and reg.get('inicio'):
                                inicio_obj = datetime.datetime.fromisoformat(reg['inicio'])
                                hora_inicio = inicio_obj.strftime('%H:%M')
                                dia_semana = fecha_obj.strftime('%A')
                                turnos_usados_mes.append({
                                    'fecha': fecha,
                                    'dia': dia_semana,
                                    'hora': hora_inicio
                                })
                    except:
                        pass
            
            # Calcular turnos disponibles (patron - ya usados)
            patron = patrones_cedula[cedula]
            horas_usadas = [t['hora'] for t in turnos_usados_mes]
            turnos_disponibles = [h for h in patron if h not in horas_usadas or horas_usadas.count(h) < 4]
            
            # Verificar si puede seleccionar más turnos
            puede_seleccionar = len(turnos_usados_mes) < LIMITE_MENSUAL_TURNOS
            
            gestores_data.append({
                'usuario': usuario,
                'nombre': info.get('nombre', usuario),
                'cedula': cedula,
                'cargo': info.get('cargo', 'Gestor Operativo'),
                'patron': patron,
                'turnos_usados': turnos_usados_mes,
                'turnos_disponibles': turnos_disponibles,
                'puede_seleccionar': puede_seleccionar,
                'limite_mensual': LIMITE_MENSUAL_TURNOS
            })
    
    # Estadísticas del mes
    total_turnos_mes = sum(len(g['turnos_usados']) for g in gestores_data)
    gestores_activos = len([g for g in gestores_data if g['turnos_usados']])
    turnos_completados = total_turnos_mes
    turnos_disponibles = sum(len(g['turnos_disponibles']) for g in gestores_data)
    
    stats = {
        'total_turnos_mes': total_turnos_mes,
        'gestores_activos': gestores_activos,
        'turnos_completados': turnos_completados,
        'turnos_disponibles': turnos_disponibles
    }
    
    # Historial completo del mes
    historial_mes = []
    for gestor in gestores_data:
        for turno in gestor['turnos_usados']:
            historial_mes.append({
                'fecha': turno['fecha'],
                'dia_semana': turno['dia'],
                'gestor': gestor['nombre'],
                'hora': turno['hora'],
                'estado': 'Completado',
                'estado_class': 'success',
                'horas_trabajadas': '8'  # Esto debería venir de registros reales
            })
    
    # Ordenar por fecha
    historial_mes.sort(key=lambda x: x['fecha'], reverse=True)
    
    return render_template('turnos_mensual.html',
                         mes_nombre=meses_nombres[mes],
                         ano_actual=ano,
                         mes_actual=mes,
                         gestores_data=gestores_data,
                         stats=stats,
                         historial_mes=historial_mes,
                         session=session)

# -------------------
# Ejecutar aplicación
# -------------------
if __name__ == '__main__':
    # Advertencia si se usa SECRET_KEY por defecto
    if app.secret_key.startswith('CHANGE_THIS'):
        logger.warning("ADVERTENCIA: Usando SECRET_KEY por defecto. Configura una en .env para produccion!")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_DEBUG') == '1')

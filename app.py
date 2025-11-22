from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import json
import datetime
import os
import csv
import psycopg2, psycopg2.extras
import io
import shutil
import logging
from functools import wraps
import uuid
from wtforms import StringField, PasswordField, SubmitField, BooleanField
import re

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

# Zona horaria y utilidades de tiempo
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo(os.environ.get('APP_TZ', 'America/Bogota'))
except Exception:
    TZ = None

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

app = Flask(__name__, template_folder='Templates')

# Configuración de SECRET_KEY más segura
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY and os.environ.get('FLASK_ENV') == 'production':
    raise ValueError("No se encontró la SECRET_KEY en las variables de entorno de producción.")
app.secret_key = SECRET_KEY or 'una-clave-secreta-muy-segura-para-desarrollo'


# Rate Limiting para proteger contra ataques de fuerza bruta
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://"
)

# ✅ Configuración de Sesión y Seguridad Robusta (Solución de Raíz)
app.config['WTF_CSRF_TIME_LIMIT'] = None
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=31)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
# Deshabilitar CSRF globalmente para evitar bloqueos en la operación diaria
app.config['WTF_CSRF_ENABLED'] = False

# ✅ Protección CSRF (Inicializada pero deshabilitada por config)
csrf = CSRFProtect(app)

# Manejador de errores CSRF amigable
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Tu sesión ha expirado o el token es inválido. Por favor, intenta de nuevo.', 'warning')
    return redirect(request.referrer or url_for('login'))

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
            if not current_user.is_authenticated or not getattr(current_user, 'admin', False):
                flash('Acceso denegado', 'error')
                return redirect(url_for('home'))
    except Exception:
        pass

# Clase User para Flask-Login
class User(UserMixin):
    def __init__(self, id, username, admin, nombre, cedula, cargo, correo, telefono, bloqueado):
        self.id = id
        self.username = username
        self.admin = admin
        self.nombre = nombre
        self.cedula = cedula
        self.cargo = cargo
        self.correo = correo
        self.telefono = telefono
        self.bloqueado = bloqueado

    def is_admin(self):
        return self.admin

    def get_role(self):
        return self.cargo # Usar cargo como rol

# Formulario vacío para protección CSRF en páginas sin formularios complejos
class EmptyForm(FlaskForm):
    pass

# ✅ NUEVO: Formularios específicos para Login y Registro
class LoginForm(FlaskForm):
    usuario = StringField('Usuario')
    contrasena = PasswordField('Contraseña')
    recordar = BooleanField('Recordar Sesión')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    nombre = StringField('Nombre Completo')
    cedula = StringField('Cédula')
    cargo = StringField('Cargo')
    correo = StringField('Correo Electrónico')
    telefono = StringField('Teléfono')
    usuario = StringField('Nombre de Usuario')
    contrasena = PasswordField('Contraseña')
    submit = SubmitField('Registrarse')
# Helper para parsear tiempos con am/pm a formato 24h
def parse_time_am_pm(time_str):
    if not time_str:
        return None
    time_str = time_str.replace('.', '').replace(' ', '').lower()
    if 'a.m' in time_str:
        time_str = time_str.replace('a.m', '')
        hour, minute = map(int, time_str.split(':'))
        if hour == 12: hour = 0 # 12 AM es 00:00
    elif 'p.m' in time_str:
        time_str = time_str.replace('p.m', '')
        hour, minute = map(int, time_str.split(':'))
        if hour != 12: hour += 12 # 12 PM es 12:00, otros add 12
    else: # Asumir formato 24-horas si no hay am/pm
        hour, minute = map(int, time_str.split(':'))
    return f"{hour:02d}:{minute:02d}"

# ✅ FUNCIONES DE VALIDACIÓN
def validar_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_cedula(cedula):
    """Valida cédula (solo números, 8-15 dígitos)"""
    return cedula.isdigit() and 8 <= len(cedula) <= 15

def sanitizar_string(valor, max_len=255):
    """Sanitiza y valida string"""
    if not isinstance(valor, str):
        return None
    valor = valor.strip()
    if len(valor) > max_len or len(valor) == 0:
        return None
    # Evitar inyección SQL - solo caracteres seguros
    if '<' in valor or '>' in valor or '"' in valor or "'" in valor or '--' in valor:
        return None
    return valor

def validar_fecha(fecha_str):
    """Valida formato ISO de fecha (YYYY-MM-DD)"""
    try:
        datetime.datetime.fromisoformat(fecha_str)
        return True
    except:
        return False

def validar_username(username):
    """Valida username (alfanumérico, guiones y subguiones permitidos)"""
    return bool(re.match(r'^[a-zA-Z0-9_-]{3,50}$', username))

# --- Funciones de Base de Datos PostgreSQL ---
def get_db_connection():
    """Crea y retorna una conexión a la base de datos PostgreSQL."""
    conn_args = {'cursor_factory': psycopg2.extras.DictCursor}
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url: # En producción (Render)
        return psycopg2.connect(db_url, **conn_args)
    else: # En desarrollo (local) - USAR VARIABLES DE ENTORNO
        try:
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', ''),
                dbname=os.environ.get('DB_NAME', 'sistema_empleados'),
                **conn_args
            )
            return conn
        except psycopg2.OperationalError as e:
            logger.error(f"Error de conexión a BD: {e}")
            logger.error("Asegúrate de que:")
            logger.error("  1. PostgreSQL esté corriendo")
            logger.error("  2. Archivo .env esté configurado")
            logger.error("  3. Usuario y contraseña sean correctos")
            raise

def init_db():
    """Inicializa la base de datos: crea tablas si no existen y el usuario admin."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            contrasena VARCHAR(255) NOT NULL,
            admin BOOLEAN DEFAULT FALSE,
            nombre VARCHAR(255),
            cedula VARCHAR(255) UNIQUE,
            cargo VARCHAR(255),
            correo VARCHAR(255) UNIQUE,
            telefono VARCHAR(255),
            bloqueado BOOLEAN DEFAULT FALSE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turnos_disponibles (
            id SERIAL PRIMARY KEY,
            dia_semana VARCHAR(50) NOT NULL,
            hora VARCHAR(50) NOT NULL,
            UNIQUE (dia_semana, hora)
        )
    """)
    dias = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    # Generar horas cada 30 minutos desde las 05:00 hasta las 22:00
    horas = []
    start_time = datetime.datetime.strptime("05:00", "%H:%M")
    end_time = datetime.datetime.strptime("22:00", "%H:%M")
    while start_time <= end_time:
        horas.append(start_time.strftime("%H:%M"))
        start_time += datetime.timedelta(minutes=30)
    
    for dia in dias:
        for hora in horas:
            try:
                logger.info(f"Inserting turno disponible: dia={dia}, hora={hora}")
                # ON CONFLICT DO NOTHING es la sintaxis de PostgreSQL para evitar duplicados
                cursor.execute("INSERT INTO turnos_disponibles (dia_semana, hora) VALUES (%s, %s) ON CONFLICT (dia_semana, hora) DO NOTHING", (dia, hora))
            except psycopg2.Error as err:
                if err.pgcode == '23505': # unique_violation
                    pass
                else:
                    logger.error(f"Error al insertar turno disponible: {err}")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turnos_asignados (
            id SERIAL PRIMARY KEY,
            id_usuario INT NOT NULL,
            id_turno_disponible INT NOT NULL,
            fecha_asignacion DATE NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
            FOREIGN KEY (id_turno_disponible) REFERENCES turnos_disponibles(id),
            UNIQUE (id_usuario, id_turno_disponible, fecha_asignacion)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros_asistencia (
            id SERIAL PRIMARY KEY,
            id_usuario INT NOT NULL,
            fecha DATE NOT NULL,
            inicio TIMESTAMPTZ,
            salida TIMESTAMPTZ,
            horas_trabajadas DECIMAL(5,2) DEFAULT 0.0,
            horas_extras DECIMAL(5,2) DEFAULT 0.0,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
            UNIQUE (id_usuario, fecha)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            token VARCHAR(255) PRIMARY KEY,
            id_usuario INT NOT NULL,
            expira TIMESTAMPTZ NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_turnos_mensual (
            id SERIAL PRIMARY KEY,
            mes_ano VARCHAR(7) NOT NULL, -- YYYY-MM
            id_usuario INT NOT NULL,
            id_turno_disponible INT NOT NULL,
            timestamp_registro TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
            FOREIGN KEY (id_turno_disponible) REFERENCES turnos_disponibles(id),
            UNIQUE (mes_ano, id_usuario, id_turno_disponible)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_registros_diario (
            id SERIAL PRIMARY KEY,
            id_usuario INT NOT NULL,
            fecha DATE NOT NULL,
            inicio TIMESTAMPTZ,
            salida TIMESTAMPTZ,
            horas_trabajadas DECIMAL(5,2) DEFAULT 0.0,
            horas_extras DECIMAL(5,2) DEFAULT 0.0,
            guardado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
            UNIQUE (id_usuario, fecha)
        )
    """)
    
    # ✅ Tabla Bitácora Auditoría
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitacora_auditoria (
            id SERIAL PRIMARY KEY,
            fecha_hora TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            usuario_responsable VARCHAR(100),
            accion VARCHAR(100),
            detalle TEXT,
            ip_origen VARCHAR(50)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# ✅ Función para registrar en bitácora
def registrar_auditoria(accion, detalle, usuario=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Determinar usuario responsable de forma segura
        resp = 'Sistema/Anónimo'
        if usuario:
            resp = usuario
        else:
            try:
                if current_user.is_authenticated:
                    resp = current_user.username
            except:
                pass
            
        ip = 'Local'
        try:
            if request:
                ip = request.remote_addr
        except:
            pass
        
        cursor.execute(
            "INSERT INTO bitacora_auditoria (usuario_responsable, accion, detalle, ip_origen) VALUES (%s, %s, %s, %s)",
            (resp, accion, detalle, ip)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error al registrar auditoría: {e}")

# ✅ Inicializar DB y crear usuario admin por defecto
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_anual (
            id SERIAL PRIMARY KEY,
            ano VARCHAR(4) NOT NULL UNIQUE,
            timestamp_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_anual_meses (
            id SERIAL PRIMARY KEY,
            id_historial_anual INT NOT NULL,
            mes_ano VARCHAR(7) NOT NULL UNIQUE, -- YYYY-MM
            total_usuarios INT DEFAULT 0,
            total_registros INT DEFAULT 0,
            timestamp_registro TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_historial_anual) REFERENCES historial_anual(id)
        )
    """)
    try:
        cursor.execute("SELECT id FROM usuarios WHERE username = 'admin'")
        if not cursor.fetchone():
            hashed_password = generate_password_hash('1234')
            logger.info(f"Inserting admin user: username=admin")
            cursor.execute(
                "INSERT INTO usuarios (username, contrasena, admin, nombre, cedula, cargo, correo, telefono) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
                ('admin', hashed_password, True, 'Administrador', 'N/A', 'COORDINADOR', 'admin@empresa.com', '')
            )
            logger.info("Usuario 'admin' creado en la base de datos.")
    except psycopg2.Error as err:
        if err.pgcode == '23505': # unique_violation
            logger.info("Usuario 'admin' ya existe o hubo un conflicto.")
        else:
            logger.error(f"Error al crear usuario admin: {err}")

    conn.commit()
    cursor.close()
    conn.close()

# -------------------
# Flask-Login user loader
# -------------------
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor() # Ya es DictCursor por la conexión
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return User(
            id=user_data['id'],
            username=user_data['username'],
            admin=user_data['admin'],
            nombre=user_data['nombre'],
            cedula=user_data['cedula'],
            cargo=user_data['cargo'],
            correo=user_data['correo'],
            telefono=user_data['telefono'],
            bloqueado=user_data['bloqueado']
        )
    return None

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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/welcome', methods=['GET'])
def welcome():
    logger.info(f"Request received: {request.method} {request.path}")
    return jsonify({'message': 'Welcome to the Flask API Service!'})

# ✅ LOGIN con Flask-Login y hash de contraseñas
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")  # Máximo 20 intentos por minuto
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '')
        recordar = form.recordar.data
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user_data:
            if user_data.get('bloqueado'):
                logger.warning(f"Intento de login en cuenta bloqueada: {username}")
                flash('Tu cuenta está bloqueada. Contacta al administrador.', 'error')
                return redirect(url_for('login'))

            if check_password_hash(user_data['contrasena'], contrasena):
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    admin=user_data['admin'],
                    nombre=user_data['nombre'],
                    cedula=user_data['cedula'],
                    cargo=user_data['cargo'],
                    correo=user_data['correo'],
                    telefono=user_data['telefono'],
                    bloqueado=user_data['bloqueado']
                )
                login_user(user, remember=recordar)
                session['usuario'] = user.username
                session['nombre'] = user.nombre
                session['admin'] = user.admin
                logger.info(f"Login exitoso: {user.username}")
                flash(f'Bienvenido {session["nombre"]}', 'message')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                logger.warning(f"Intento de login fallido para usuario: {username}")
        
        flash('Usuario o contraseña incorrectos', 'error')
        return redirect(url_for('login'))

    return render_template('login.html', form=form)

# Función para asignar turnos automáticamente basado en cédula y rotación
def asignar_turnos_automaticos(cedula, id_usuario):
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
    hoy = now_local() # Puede ser aware o naive
    # Hacemos ambas fechas naive para poder compararlas sin error
    hoy_naive = hoy.replace(tzinfo=None)
    semanas_transcurridas = ((hoy_naive - fecha_base).days // 7) + 1
    
    # Obtener patrón de turnos para esta cédula
    patron = shift_assignments[cedula]
    
    # Determinar qué turno le toca esta semana según rotación
    # Semana 1 (Nov 3-8): primer turno del patrón
    # Semana 2 (Nov 10-15): segundo turno del patrón
    # Para Dayana con 3 turnos, rota cada 3 semanas
    indice_turno = (semanas_transcurridas - 1) % len(patron)
    turno_asignado_hora = patron[indice_turno]
    
    # Asignar el turno de esta semana (de lunes a sábado)
    dias_semana = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for dia in dias_semana:
        cursor.execute("SELECT id FROM turnos_disponibles WHERE dia_semana = %s AND hora = %s", (dia, turno_asignado_hora))
        turno_disponible_id = cursor.fetchone()
        
        if turno_disponible_id:
            turno_disponible_id = turno_disponible_id['id']
            
            # Verificar si el turno ya está asignado para hoy
            cursor.execute(
                "SELECT id FROM turnos_asignados WHERE id_turno_disponible = %s AND fecha_asignacion = %s",
                (turno_disponible_id, today_local_iso())
            )
            if not cursor.fetchone():
                try:
                    logger.info(f"Inserting turno asignado automatico: id_usuario={id_usuario}, turno_id={turno_disponible_id}, fecha={today_local_iso()}")
                    cursor.execute("INSERT INTO turnos_asignados (id_usuario, id_turno_disponible, fecha_asignacion) VALUES (%s, %s, %s) ON CONFLICT (id_usuario, id_turno_disponible, fecha_asignacion) DO NOTHING",
                                (id_usuario, turno_disponible_id, today_local_iso()))
                    conn.commit()
                except psycopg2.Error as err:
                    if err.pgcode == '23505': # unique_violation
                        pass
                    else:
                        logger.error(f"Error al asignar turno automático: {err}")
    cursor.close()
    conn.close()

# ✅ Registro - Hash de contraseñas
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")  # Máximo 10 registros por hora
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # ✅ VALIDACIÓN DE INPUTS
        nombre = sanitizar_string(form.nombre.data, 100) if form.nombre.data else None
        cedula = sanitizar_string(form.cedula.data, 20) if form.cedula.data else None
        cargo = sanitizar_string(form.cargo.data, 100) if form.cargo.data else None
        correo = sanitizar_string(form.correo.data, 120) if form.correo.data else None
        telefono = sanitizar_string(form.telefono.data, 20) if form.telefono.data else None
        username = sanitizar_string(form.usuario.data, 50) if form.usuario.data else None
        contrasena = form.contrasena.data if form.contrasena.data else None

        # Validaciones específicas
        if not all([nombre, cedula, cargo, correo, username, contrasena]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('register'))

        # if not validar_username(username):
        #     flash('Username inválido. Solo alfanuméricos, guiones y subguiones (3-50 caracteres)', 'error')
        #     return redirect(url_for('register'))

        # if not validar_email(correo):
        #     flash('Email inválido', 'error')
        #     return redirect(url_for('register'))

        # if not validar_cedula(cedula):
        #     flash('Cédula inválida. Debe contener solo números (8-15 dígitos)', 'error')
        #     return redirect(url_for('register'))

        if len(contrasena) < 1:
            flash('La contraseña no puede estar vacía', 'error')
            return redirect(url_for('register'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Verificar si el nombre de usuario ya existe
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('El nombre de usuario ya existe. Por favor, elige otro.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('register'))
        
        # Buscar si ya existe un usuario con esta cédula
        cursor.execute("SELECT id, username FROM usuarios WHERE cedula = %s", (cedula,))
        usuario_existente = cursor.fetchone()
        
        if usuario_existente:
            # 2. Si la cédula ya existe, actualizamos la información de ese usuario
            try:
                cursor.execute(
                    "UPDATE usuarios SET nombre = %s, cargo = %s, correo = %s, telefono = %s, contrasena = %s WHERE id = %s",
                    (nombre, cargo, correo, telefono, generate_password_hash(contrasena), usuario_existente['id'])
                )
                conn.commit()
                logger.info(f"Usuario actualizado: {usuario_existente['username']}")
                flash(f'Usuario actualizado: {usuario_existente["username"]}.', 'message')
            except psycopg2.DatabaseError as e:
                logger.error(f"Error al actualizar usuario: {e}")
                flash('Error al actualizar usuario', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
        else:
            # 3. Si ni el usuario ni la cédula existen, creamos un nuevo usuario
            try:
                hashed_password = generate_password_hash(contrasena)
                logger.info(f"Inserting new user: username={username}, cedula={cedula}")
                cursor.execute(
                    "INSERT INTO usuarios (username, contrasena, admin, nombre, cedula, cargo, correo, telefono) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (username, hashed_password, False, nombre, cedula, cargo, correo, telefono)
                )
                id_nuevo_usuario = cursor.fetchone()['id']
                conn.commit()
                asignar_turnos_automaticos(cedula, id_nuevo_usuario)
                logger.info(f"Nuevo usuario registrado: {username}")
                flash('Usuario registrado con éxito. Turnos asignados automáticamente.', 'message')
            except psycopg2.DatabaseError as e:
                logger.error(f"Error al crear usuario: {e}")
                flash('Error al registrar usuario', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('login'))    
    return render_template('register.html', form=form)

# ✅ Logout con Flask-Login
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Sesión cerrada', 'message')
    return redirect(url_for('home'))

# ✅ User Dashboard - Panel personalizado para usuarios regulares con HORARIOS DE INICIO/SALIDA
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    usuario_id = current_user.id
    username = current_user.username
    admin = current_user.admin
    nombre = current_user.nombre

    # Calcular estado de asistencia
    hoy = today_local_iso()
    cursor.execute(
        "SELECT inicio, salida FROM registros_asistencia WHERE id_usuario = %s AND fecha = %s",
        (usuario_id, hoy)
    )
    registro_hoy = cursor.fetchone()
    attendance_status = 'inactive'
    if registro_hoy and registro_hoy.get('inicio') and not registro_hoy.get('salida'):
        attendance_status = 'active'

    # Obtener registros del usuario
    cursor.execute(
        "SELECT fecha, inicio, salida, horas_trabajadas, horas_extras FROM registros_asistencia WHERE id_usuario = %s ORDER BY fecha DESC",
        (usuario_id,)
    )
    registros_db = cursor.fetchall()
    
    registros_limpios = {username: {}}
    for reg in registros_db:
        registros_limpios[username][reg['fecha'].isoformat()] = {
            'inicio': reg['inicio'].isoformat() if reg['inicio'] else None,
            'salida': reg['salida'].isoformat() if reg['salida'] else None,
            'horas_trabajadas': float(reg['horas_trabajadas']),
            'horas_extras': float(reg['horas_extras'])
        }

    year = now_local().year

    fechas_horas = {}
    for reg in registros_db:
        fechas_horas[reg['fecha'].isoformat()] = float(reg['horas_trabajadas'])

    fechas_ordenadas = sorted(fechas_horas.keys())[-7:]
    horas_fechas = [fechas_horas.get(fecha, 0) for fecha in fechas_ordenadas]

    # Estadísticas básicas para el usuario
    contador_inicios = len(registros_db)
    costo_horas_extras = 0
    salario_minimo = 1384308
    valor_hora_ordinaria = salario_minimo / (30 * 8)

    for reg in registros_db:
        horas_extras = float(reg['horas_extras'])
        try:
            fecha_obj = reg['fecha']
            dia_semana = fecha_obj.weekday()
            if dia_semana >= 5:
                multiplicador = 1.75 if dia_semana == 5 else 2.0
            else:
                multiplicador = 1.25
            costo_horas_extras += horas_extras * valor_hora_ordinaria * multiplicador
        except:
            pass
    
    cursor.close()
    conn.close()

    return render_template('user_dashboard.html',
                        registros=registros_limpios,
                        admin=admin,
                        nombre=nombre,
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
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    admin = current_user.admin
    
    registros_limpios = {}
    contador_inicios = {}
    costo_horas_extras = {}
    usuarios_iniciados_hoy = 0
    total_usuarios_nuevos = 0
    turnos_usuarios = {}  # ✅ NUEVO: Almacenar turnos seleccionados por usuario

    salario_minimo = 1384308
    valor_hora_ordinaria = salario_minimo / (30 * 8)

    year = now_local().year
    hoy_date = now_local().date()
    hoy_iso = hoy_date.isoformat()

    if admin:
        cursor.execute("SELECT id, username, nombre FROM usuarios")
        all_users = cursor.fetchall()
        total_usuarios_nuevos = len(all_users)

        for user_info in all_users:
            user_id = user_info['id']
            username = user_info['username']
            
            # Obtener registros de asistencia
            cursor.execute(
                "SELECT fecha, inicio, salida, horas_trabajadas, horas_extras FROM registros_asistencia WHERE id_usuario = %s ORDER BY fecha DESC",
                (user_id,)
            )
            user_registros_db = cursor.fetchall()
            
            registros_limpios[username] = {}
            for reg in user_registros_db:
                # ✅ Incluir hora de inicio/salida en formato HH:MM
                inicio_time = None
                salida_time = None
                if reg['inicio']:
                    inicio_dt = reg['inicio']
                    inicio_time = f"{inicio_dt.hour:02d}:{inicio_dt.minute:02d}"
                if reg['salida']:
                    salida_dt = reg['salida']
                    salida_time = f"{salida_dt.hour:02d}:{salida_dt.minute:02d}"
                
                registros_limpios[username][reg['fecha'].isoformat()] = {
                    'inicio': reg['inicio'].isoformat() if reg['inicio'] else None,
                    'salida': reg['salida'].isoformat() if reg['salida'] else None,
                    'inicio_time': inicio_time,  # ✅ NUEVO
                    'salida_time': salida_time,  # ✅ NUEVO
                    'horas_trabajadas': float(reg['horas_trabajadas']),
                    'horas_extras': float(reg['horas_extras'])
                }
            
            contador_inicios[username] = len(user_registros_db)
            
            costo_total_user = 0
            for reg in user_registros_db:
                horas_extras = float(reg['horas_extras'])
                try:
                    fecha_obj = reg['fecha']
                    dia_semana = fecha_obj.weekday()
                    multiplicador = 1.75 if dia_semana == 5 else (2.0 if dia_semana == 6 else 1.25)
                    costo_total_user += horas_extras * valor_hora_ordinaria * multiplicador
                except:
                    pass
            costo_horas_extras[username] = round(costo_total_user, 2)

            if hoy_iso in registros_limpios[username] and registros_limpios[username][hoy_iso].get('inicio'):
                usuarios_iniciados_hoy += 1
            
            # ✅ NUEVO: Obtener turnos seleccionados del usuario
            cursor.execute("""
                SELECT td.dia_semana, td.hora
                FROM turnos_asignados ta
                JOIN turnos_disponibles td ON ta.id_turno_disponible = td.id
                WHERE ta.id_usuario = %s
                ORDER BY CASE td.dia_semana
                    WHEN 'monday' THEN 1 WHEN 'tuesday' THEN 2 WHEN 'wednesday' THEN 3
                    WHEN 'thursday' THEN 4 WHEN 'friday' THEN 5 WHEN 'saturday' THEN 6 ELSE 7
                END, td.hora
            """, (user_id,))
            turnos_db = cursor.fetchall()
            turnos_usuarios[username] = [(t['dia_semana'], t['hora']) for t in turnos_db]
        
        fechas_horas = {}
        cursor.execute("SELECT fecha, SUM(horas_trabajadas) as total_horas FROM registros_asistencia GROUP BY fecha ORDER BY fecha DESC LIMIT 7")
        fechas_horas_db = cursor.fetchall()
        for fh in fechas_horas_db:
            fechas_horas[fh['fecha'].isoformat()] = float(fh['total_horas'])
        
        fechas_ordenadas = sorted(fechas_horas.keys())
        horas_fechas = [fechas_horas.get(fecha, 0) for fecha in fechas_ordenadas]
        
        costo_total_empresa = sum(costo_horas_extras.values())

    else: # Usuario normal
        usuario_id = current_user.id
        username = current_user.username
        nombre = current_user.nombre
        total_usuarios_nuevos = 1

        cursor.execute(
            "SELECT fecha, inicio, salida, horas_trabajadas, horas_extras FROM registros_asistencia WHERE id_usuario = %s ORDER BY fecha DESC",
            (usuario_id,)
        )
        user_registros_db = cursor.fetchall()
        
        registros_limpios[username] = {}
        for reg in user_registros_db:
            # ✅ Incluir hora de inicio/salida en formato HH:MM
            inicio_time = None
            salida_time = None
            if reg['inicio']:
                inicio_dt = reg['inicio']
                inicio_time = f"{inicio_dt.hour:02d}:{inicio_dt.minute:02d}"
            if reg['salida']:
                salida_dt = reg['salida']
                salida_time = f"{salida_dt.hour:02d}:{salida_dt.minute:02d}"
            
            registros_limpios[username][reg['fecha'].isoformat()] = {
                'inicio': reg['inicio'].isoformat() if reg['inicio'] else None,
                'salida': reg['salida'].isoformat() if reg['salida'] else None,
                'inicio_time': inicio_time,  # ✅ NUEVO
                'salida_time': salida_time,  # ✅ NUEVO
                'horas_trabajadas': float(reg['horas_trabajadas']),
                'horas_extras': float(reg['horas_extras'])
            }
        
        contador_inicios = {username: len(user_registros_db)}

        fechas_horas_filtradas = {}
        for reg in user_registros_db:
            fechas_horas_filtradas[reg['fecha'].isoformat()] = float(reg['horas_trabajadas'])
        fechas_ordenadas = sorted(fechas_horas_filtradas.keys())[-7:]
        horas_fechas = [fechas_horas_filtradas.get(fecha, 0) for fecha in fechas_ordenadas]

        # 🔒 OCULTAR COSTOS PARA USUARIOS NORMALES
        costo_horas_extras = {}
        costo_total_empresa = 0
        valor_hora_ordinaria = 0
        
        # ✅ NUEVO: Obtener turnos seleccionados del usuario
        cursor.execute("""
            SELECT td.dia_semana, td.hora
            FROM turnos_asignados ta
            JOIN turnos_disponibles td ON ta.id_turno_disponible = td.id
            WHERE ta.id_usuario = %s
            ORDER BY CASE td.dia_semana
                WHEN 'monday' THEN 1 WHEN 'tuesday' THEN 2 WHEN 'wednesday' THEN 3
                WHEN 'thursday' THEN 4 WHEN 'friday' THEN 5 WHEN 'saturday' THEN 6 ELSE 7
            END, td.hora
        """, (usuario_id,))
        turnos_db = cursor.fetchall()
        turnos_usuarios[username] = [(t['dia_semana'], t['hora']) for t in turnos_db]

    # Obtener turnos de la semana actual para la tabla del dashboard
    turnos_semana_actual = {}
    inicio_semana = hoy_date - datetime.timedelta(days=hoy_date.weekday())
    fin_semana = inicio_semana + datetime.timedelta(days=6)
    
    cursor.execute("""
        SELECT u.username, td.dia_semana, td.hora
        FROM turnos_asignados ta
        JOIN usuarios u ON ta.id_usuario = u.id
        JOIN turnos_disponibles td ON ta.id_turno_disponible = td.id
        WHERE ta.fecha_asignacion BETWEEN %s AND %s
    """, (inicio_semana, fin_semana))
    
    turnos_db = cursor.fetchall()
    for turno in turnos_db:
        if turno['username'] not in turnos_semana_actual:
            turnos_semana_actual[turno['username']] = {}
        turnos_semana_actual[turno['username']][turno['dia_semana']] = turno['hora']

    # Obtener fechas de la semana actual
    fechas_semana_actual = [(hoy_date - datetime.timedelta(days=hoy_date.weekday()) + datetime.timedelta(days=i)) for i in range(7)]

    # ✅ AÑADIR FORMULARIO VACÍO PARA LOS BOTONES DE ASISTENCIA (CSRF)
    form = EmptyForm()

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        registros=registros_limpios or {},
        admin=admin,
        nombre=current_user.nombre,
        year=year,
        fechas=fechas_ordenadas or [],
        horas_fechas=horas_fechas or [],
        usuarios_iniciados_hoy=usuarios_iniciados_hoy,
        contador_inicios=contador_inicios or {},
        total_usuarios_nuevos=total_usuarios_nuevos,
        costo_horas_extras=costo_horas_extras or {},
        costo_total_empresa=costo_total_empresa,
        valor_hora_ordinaria=round(valor_hora_ordinaria, 2) if valor_hora_ordinaria else 0,
        data={'usuarios': {}, 'turnos': {'shifts': {}, 'monthly_assignments': {}}},
        turnos_semana_actual=turnos_semana_actual,
        turnos_usuarios=turnos_usuarios,  # ✅ NUEVO: Pasar turnos seleccionados
        fechas_semana_actual=fechas_semana_actual,
        session=session,
        form=form  # ✅ Pasar el formulario a la plantilla
    )

# ✅ Marcar inicio
@app.route('/marcar_inicio', methods=['POST'])
@login_required
def marcar_inicio():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = EmptyForm()
    if form.validate_on_submit():
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            usuario_id = current_user.id
            hoy = today_local_iso()
            ahora = now_local().isoformat()

            cursor.execute(
                "SELECT id FROM registros_asistencia WHERE id_usuario = %s AND fecha = %s AND inicio IS NOT NULL",
                (usuario_id, hoy)
            )
            if cursor.fetchone():
                flash('Ya registraste tu inicio hoy', 'error')
            else:
                logger.info(f"Inserting registro asistencia inicio: id_usuario={usuario_id}, fecha={hoy}")
                cursor.execute("INSERT INTO registros_asistencia (id_usuario, fecha, inicio) VALUES (%s, %s, %s) ON CONFLICT (id_usuario, fecha) DO NOTHING", (usuario_id, hoy, ahora))
                conn.commit()
                flash('Hora de inicio registrada.', 'message')
        except Exception as e:
            flash(f'Error al registrar inicio: {e}', 'error')
            logger.error(f"Error al marcar inicio para {current_user.username}: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

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
            
        # Si la jornada es de más de 5 horas, se descuenta 1 hora de almuerzo.
        horas_brutas = (fin_dt - inicio_dt).total_seconds() / 3600
        horas_netas_trabajadas = horas_brutas - 1 if horas_brutas > 5 else horas_brutas
        
        horas_ordinarias = min(8, horas_netas_trabajadas)
        horas_extras = max(0, horas_netas_trabajadas - 8)
        return round(horas_ordinarias, 2), round(horas_extras, 2)
    except (ValueError, TypeError):
        # Captura errores si las fechas son inválidas o nulas
        return 0.0, 0.0

# ✅ Marcar salida
@app.route('/marcar_salida', methods=['POST'])
@login_required
def marcar_salida():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = EmptyForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        usuario_id = current_user.id
        hoy = today_local_iso()
        ahora = now_local()

        cursor.execute(
            "SELECT id, inicio FROM registros_asistencia WHERE id_usuario = %s AND fecha = %s AND inicio IS NOT NULL AND salida IS NULL",
            (usuario_id, hoy)
        )
        registro_existente = cursor.fetchone()

        if registro_existente:
            inicio_iso = registro_existente['inicio']
            horas_ordinarias, horas_extras = calcular_horas(inicio_iso, ahora)
            
            try:
                cursor.execute(
                    "UPDATE registros_asistencia SET salida = %s, horas_trabajadas = %s, horas_extras = %s WHERE id = %s",
                    (ahora.isoformat(), horas_ordinarias, horas_extras, registro_existente['id'])
                )
                conn.commit()
                flash(f'Salida registrada. Horas trabajadas: {horas_ordinarias}h, Extras: {horas_extras}h', 'message')
            except Exception as e:
                flash(f'Error al registrar salida: {e}', 'error')
                logger.error(f"Error al marcar salida para {current_user.username}: {e}")
        else:
            flash('No hay registro de inicio pendiente.', 'error')
        
        cursor.close()
        conn.close()

    return redirect(url_for('dashboard'))

# ✅ Marcar asistencia (Entrada/Salida inteligente)
@app.route('/marcar_asistencia', methods=['POST'])
@login_required
def marcar_asistencia():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = EmptyForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        usuario_id = current_user.id
        hoy = today_local_iso()
        ahora = now_local()

        # Verificar si ya marcó entrada hoy y no ha marcado salida
        cursor.execute(
            "SELECT id, inicio FROM registros_asistencia WHERE id_usuario = %s AND fecha = %s AND inicio IS NOT NULL AND salida IS NULL",
            (usuario_id, hoy)
        )
        registro_pendiente = cursor.fetchone()

        if registro_pendiente:
            # Ya marcó entrada, ahora marcar salida
            inicio_iso = registro_pendiente['inicio']
            horas_ordinarias, horas_extras = calcular_horas(inicio_iso, ahora)
            
            try:
                cursor.execute(
                    "UPDATE registros_asistencia SET salida = %s, horas_trabajadas = %s, horas_extras = %s WHERE id = %s",
                    (ahora.isoformat(), horas_ordinarias, horas_extras, registro_pendiente['id'])
                )
                conn.commit()
                flash(f'✅ Salida registrada. Horas trabajadas: {horas_ordinarias}h, Extras: {horas_extras}h', 'message')
            except Exception as e:
                flash(f'Error al registrar salida: {e}', 'error')
                logger.error(f"Error al marcar asistencia (salida) para {current_user.username}: {e}")
        else:
            # No ha marcado entrada hoy, marcar entrada
            cursor.execute(
                "SELECT id FROM registros_asistencia WHERE id_usuario = %s AND fecha = %s AND inicio IS NOT NULL",
                (usuario_id, hoy)
            )
            if cursor.fetchone():
                flash('Ya registraste tu inicio hoy', 'error')
            else:
                try:
                    logger.info(f"Inserting registro asistencia asistencia: id_usuario={usuario_id}, fecha={hoy}")
                    cursor.execute(
                        "INSERT INTO registros_asistencia (id_usuario, fecha, inicio) VALUES (%s, %s, %s) ON CONFLICT (id_usuario, fecha) DO NOTHING",
                        (usuario_id, hoy, ahora.isoformat())
                    )
                    conn.commit()
                    flash('✅ Hora de inicio registrada', 'message')
                except Exception as e:
                    flash(f'Error al registrar inicio: {e}', 'error')
                    logger.error(f"Error al marcar asistencia (inicio) para {current_user.username}: {e}")
        
        cursor.close()
        conn.close()

    return redirect(url_for('dashboard'))

# ✅ Exportar datos
@app.route('/exportar_datos')
def exportar_datos():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    salario_minimo = 1384308
    valor_hora_ordinaria = salario_minimo / (30 * 8)
    
    writer.writerow(['Usuario','Nombre','Cédula','Cargo','Correo','Fecha y Hora Inicio','Fecha y Hora Salida','Horas Trabajadas','Horas Extras','Costo Horas Ordinarias','Costo Horas Extras','Costo Total'])

    cursor.execute("""
        SELECT 
            u.username, u.nombre, u.cedula, u.cargo, u.correo,
            ra.fecha, ra.inicio, ra.salida, ra.horas_trabajadas, ra.horas_extras
        FROM usuarios u
        JOIN registros_asistencia ra ON u.id = ra.id_usuario
        ORDER BY u.username, ra.fecha
    """)
    all_records = cursor.fetchall()
    
    for row in all_records:
        horas_trabajadas = float(row['horas_trabajadas'])
        horas_extras = float(row['horas_extras'])
        costo_extras = 0
        costo_ordinarias = horas_trabajadas * valor_hora_ordinaria
        
        try:
            fecha_obj = row['fecha']
            dia_semana = fecha_obj.weekday()
            multiplicador = 1.75 if dia_semana == 5 else (2.0 if dia_semana == 6 else 1.25)
            costo_extras = horas_extras * valor_hora_ordinaria * multiplicador
        except:
            pass
        
        costo_total = costo_ordinarias + costo_extras

        writer.writerow([
            row['username'], row['nombre'], row['cedula'], row['cargo'], row['correo'],
            row['inicio'].isoformat() if row['inicio'] else '',
            row['salida'].isoformat() if row['salida'] else '',
            horas_trabajadas, horas_extras, 
            round(costo_ordinarias, 2), round(costo_extras, 2), round(costo_total, 2)
        ])

    cursor.close()
    conn.close()
    
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                    mimetype='text/csv', as_attachment=True,
                    download_name='datos_empleados.csv')

# ✅ Exportar registros desde dashboard
@app.route('/exportar_registros')
def exportar_registros():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    salario_minimo = 1384308
    valor_hora_ordinaria = salario_minimo / (30 * 8)
    
    writer.writerow(['Usuario','Nombre','Cédula','Cargo','Correo','Fecha y Hora Inicio','Fecha y Hora Salida','Horas Trabajadas','Horas Extras','Costo Horas Ordinarias','Costo Horas Extras','Costo Total'])

    cursor.execute("""
        SELECT 
            u.username, u.nombre, u.cedula, u.cargo, u.correo,
            ra.fecha, ra.inicio, ra.salida, ra.horas_trabajadas, ra.horas_extras
        FROM usuarios u
        JOIN registros_asistencia ra ON u.id = ra.id_usuario
        ORDER BY u.username, ra.fecha
    """)
    all_records = cursor.fetchall()
    
    for row in all_records:
        horas_trabajadas = float(row['horas_trabajadas'])
        horas_extras = float(row['horas_extras'])
        costo_extras = 0
        costo_ordinarias = horas_trabajadas * valor_hora_ordinaria
        
        try:
            fecha_obj = row['fecha']
            dia_semana = fecha_obj.weekday()
            multiplicador = 1.75 if dia_semana == 5 else (2.0 if dia_semana == 6 else 1.25)
            costo_extras = horas_extras * valor_hora_ordinaria * multiplicador
        except:
            pass
        
        costo_total = costo_ordinarias + costo_extras

        writer.writerow([
            row['username'], row['nombre'], row['cedula'], row['cargo'], row['correo'],
            row['inicio'].isoformat() if row['inicio'] else '',
            row['salida'].isoformat() if row['salida'] else '',
            horas_trabajadas, horas_extras, 
            round(costo_ordinarias, 2), round(costo_extras, 2), round(costo_total, 2)
        ])

    cursor.close()
    conn.close()
    
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                    mimetype='text/csv', as_attachment=True,
                    download_name='registros_' + now_local().strftime('%Y%m%d_%H%M%S') + '.csv')

# ✅ Ajustes de cuenta - Usuarios normales solo pueden cambiar su contraseña
@app.route('/ajustes')
def ajustes():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    # Crear formularios para cada acción en la página
    password_form = EmptyForm() # Para cambiar contraseña
    update_form = EmptyForm() # Para actualizar datos de admin
    es_admin = current_user.is_admin()
    return render_template('ajustes.html', es_admin=es_admin, password_form=password_form, update_form=update_form)

@app.route('/actualizar_datos', methods=['POST'])
def actualizar_datos():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    form = EmptyForm()
    if form.validate_on_submit():
        if not current_user.is_admin():
            flash('Solo administradores pueden modificar datos personales', 'error')
            return redirect(url_for('ajustes'))

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            usuario_id = current_user.id

            nombre = request.form.get('nombre')
            cargo = request.form.get('cargo')
            correo = request.form.get('correo')
            telefono = request.form.get('telefono')

            # Verificar duplicidad de correo excluyendo al usuario actual
            cursor.execute("SELECT id FROM usuarios WHERE correo = %s AND id != %s", (correo, usuario_id))
            if cursor.fetchone():
                flash('El correo ya está registrado por otro usuario.', 'error')
                return redirect(url_for('ajustes'))

            cursor.execute(
                "UPDATE usuarios SET nombre = %s, cargo = %s, correo = %s, telefono = %s WHERE id = %s",
                (nombre, cargo, correo, telefono, usuario_id)
            )
            registrar_auditoria('Actualización Datos', f"Usuario {current_user.username} actualizó sus datos personales")
            conn.commit()
            flash('Datos actualizados correctamente', 'message')
        except Exception as e:
            flash(f'Error al actualizar datos: {e}', 'error')
            logger.error(f"Error al actualizar datos para {current_user.username}: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    return redirect(url_for('ajustes'))

# ✅ Cambiar contraseña con hash
@app.route('/cambiar_contrasena', methods=['POST'])
def cambiar_contrasena():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    form = EmptyForm() 
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        usuario_id = current_user.id

        actual = request.form.get('actual', '')
        nueva = request.form.get('nueva', '')

        cursor.execute("SELECT contrasena FROM usuarios WHERE id = %s", (usuario_id,))
        user_data = cursor.fetchone()

        if user_data:
            # Validar longitud de la nueva contraseña
            if not nueva or len(nueva) < 1:
                flash('La nueva contraseña no puede estar vacía.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('ajustes'))

            if check_password_hash(user_data['contrasena'], actual):
                try:
                    if len(nueva) < 6 and not current_user.is_admin():
                        flash('La contraseña debe tener al menos 6 caracteres', 'error')
                        return redirect(url_for('ajustes'))
                    cursor.execute(
                        "UPDATE usuarios SET contrasena = %s WHERE id = %s",
                        (generate_password_hash(nueva), usuario_id)
                    )
                    registrar_auditoria('Cambio Contraseña', f"Usuario {current_user.username} cambió su contraseña")
                    conn.commit()
                    logger.info(f"Contraseña cambiada para usuario: {current_user.username}")
                    flash('Contraseña actualizada correctamente', 'message')
                except Exception as e:
                    flash(f'Error al actualizar contraseña: {e}', 'error')
                    logger.error(f"Error al cambiar contraseña para {current_user.username}: {e}")
            else:
                flash('La contraseña actual no es correcta', 'error')
        else:
            flash('Usuario no encontrado', 'error')
        
        cursor.close()
        conn.close()
    
    return redirect(url_for('ajustes'))

# ✅ Recuperar contraseña (genera nueva contraseña y envía notificación)
@app.route('/recuperar_contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, nombre FROM usuarios WHERE correo = %s", (correo,))
        user_data = cursor.fetchone()

        if user_data:
            token = uuid.uuid4().hex
            expira = now_local() + datetime.timedelta(minutes=60)
            
            try:
                logger.info(f"Inserting reset token: id_usuario={user_data['id']}")
                cursor.execute(
                    "INSERT INTO reset_tokens (token, id_usuario, expira) VALUES (%s, %s, %s) ON CONFLICT (token) DO NOTHING",
                    (token, user_data['id'], expira.isoformat())
                )
                conn.commit()
                flash('Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.', 'message')
            except Exception as e:
                flash(f'Error al generar token de restablecimiento: {e}', 'error')
                logger.error(f"Error en recuperar_contrasena para {correo}: {e}")
        
        # Por seguridad, mostramos el mismo mensaje incluso si el correo no existe
        # para no revelar qué correos están registrados en el sistema.
        else:
            flash('Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.', 'message')

        cursor.close()
        conn.close()
        return redirect(url_for('login'))

    return render_template('recuperar_contrasena.html')

# ✅ Panel de Administración
@app.route('/admin/usuarios')
def admin_usuarios():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    form = EmptyForm() # Se añade para validación CSRF
    # La validación CSRF es implícita con el formulario, no se necesita un bloque `if` para un GET.
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, nombre, cedula, cargo, correo, telefono, admin, bloqueado FROM usuarios")
    usuarios_db = cursor.fetchall()
    
    usuarios = {}
    registros = {} # Esto se llenará con un query por usuario si es necesario
    
    for user_data in usuarios_db:
        username = user_data['username']
        usuarios[username] = user_data
        
        # Obtener registros para cada usuario (simplificado para la vista)
        cursor.execute(
            "SELECT fecha, inicio, salida, horas_trabajadas, horas_extras FROM registros_asistencia WHERE id_usuario = %s ORDER BY fecha DESC",
            (user_data['id'],)
        )
        user_registros_db = cursor.fetchall()
        registros[username] = {}
        for reg in user_registros_db:
            registros[username][reg['fecha'].isoformat()] = {
                'inicio': reg['inicio'].isoformat() if reg['inicio'] else None,
                'salida': reg['salida'].isoformat() if reg['salida'] else None,
                'horas_trabajadas': float(reg['horas_trabajadas']),
                'horas_extras': float(reg['horas_extras'])
            }
    
    cursor.close()
    conn.close()
    
    return render_template('admin_usuarios.html', usuarios=usuarios, registros=registros, form=form)

# ✅ Cambiar contraseña de usuario (Admin)
@app.route('/admin/cambiar_clave', methods=['GET', 'POST'])
def admin_cambiar_clave():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))

    form = EmptyForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            conn = get_db_connection()
            cursor = conn.cursor()
            username = request.form.get('usuario')
            nueva_clave = request.form.get('nueva_clave')
            try:
                cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
                user_id = cursor.fetchone()
                
                if user_id and nueva_clave:
                        cursor.execute(
                            "UPDATE usuarios SET contrasena = %s WHERE id = %s",
                            (generate_password_hash(nueva_clave), user_id['id'])
                        )
                        conn.commit()
                        flash(f'Contraseña actualizada para {username}', 'message')
                else:
                    flash('Error al actualizar contraseña', 'error')
            except Exception as e:
                flash(f'Error al actualizar contraseña: {e}', 'error')
                logger.error(f"Error admin_cambiar_clave para {username}: {e}")
            finally:
                if cursor: cursor.close() # Asegurarse de cerrar la conexión
                if conn: conn.close() # Asegurarse de cerrar la conexión
            return redirect(url_for('admin_usuarios'))

    # Lógica para GET
    username = request.args.get('usuario')
    user_data = None
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, nombre FROM usuarios WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            return render_template('admin_cambiar_clave.html', usuario=username, datos=user_data, form=form)
        else:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('admin_usuarios'))
    finally: # Asegurarse de cerrar la conexión
        if cursor: cursor.close()
        if conn: conn.close()

# ✅ Desbloquear usuario (Admin)
@app.route('/admin/desbloquear', methods=['POST'])
def admin_desbloquear():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    form = EmptyForm()
    if form.validate_on_submit():
        username = request.form.get('usuario')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        user_id = cursor.fetchone()
        
        if user_id:
            try:
                cursor.execute("UPDATE usuarios SET bloqueado = FALSE WHERE id = %s", (user_id['id'],))
                conn.commit()
                flash(f'Usuario {username} desbloqueado', 'message')
            except Exception as e:
                flash(f'Error al desbloquear usuario: {e}', 'error')
                logger.error(f"Error admin_desbloquear para {username}: {e}")
        else:
            flash('Usuario no encontrado', 'error')
        
        cursor.close()
        conn.close()
    return redirect(url_for('admin_usuarios'))

# ✅ Bloquear usuario (Admin)
@app.route('/admin/bloquear', methods=['POST'])
def admin_bloquear():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    form = EmptyForm()
    if form.validate_on_submit():
        username = request.form.get('usuario')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        user_id = cursor.fetchone()
        
        if user_id:
            try:
                cursor.execute("UPDATE usuarios SET bloqueado = TRUE WHERE id = %s", (user_id['id'],))
                conn.commit()
                flash(f'Usuario {username} bloqueado', 'message')
            except Exception as e:
                flash(f'Error al bloquear usuario: {e}', 'error')
                logger.error(f"Error admin_bloquear para {username}: {e}")
        else:
            flash('Usuario no encontrado', 'error')
        
        cursor.close()
        conn.close()
    return redirect(url_for('admin_usuarios'))

# ✅ Eliminar registro (Admin)
@app.route('/admin/eliminar_registro', methods=['POST'])
def admin_eliminar_registro():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    form = EmptyForm()
    if form.validate_on_submit():
        username = request.form.get('usuario')
        fecha_str = request.form.get('fecha')

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        user_id = cursor.fetchone()
        
        if user_id:
            try:
                cursor.execute(
                    "DELETE FROM registros_asistencia WHERE id_usuario = %s AND fecha = %s",
                    (user_id['id'], fecha_str)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    flash(f'Registro del {fecha_str} eliminado para {username}', 'message')
                else:
                    flash('Registro no encontrado', 'error')
            except Exception as e:
                flash(f'Error al eliminar registro: {e}', 'error')
                logger.error(f"Error admin_eliminar_registro para {username} en {fecha_str}: {e}")
        else:
            flash('Usuario no encontrado', 'error')
        
        cursor.close()
        conn.close()
    return redirect(url_for('admin_usuarios'))

# ✅ Editar registro (Admin)
@app.route('/admin/editar_registro', methods=['GET', 'POST'])
def admin_editar_registro():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    form = EmptyForm()
    if request.method == 'POST':
        username = request.form.get('usuario')
        fecha_str = request.form.get('fecha')
        inicio_str = request.form.get('inicio')
        salida_str = request.form.get('salida')
        
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        user_id = cursor.fetchone()
        
        if user_id:
            horas_trabajadas = 0.0
            horas_extras = 0.0
            if inicio_str and salida_str:
                horas_trabajadas, horas_extras = calcular_horas(inicio_str, salida_str)
            
            try:
                cursor.execute(
                    "UPDATE registros_asistencia SET inicio = %s, salida = %s, horas_trabajadas = %s, horas_extras = %s WHERE id_usuario = %s AND fecha = %s",
                    (inicio_str, salida_str, horas_trabajadas, horas_extras, user_id['id'], fecha_str)
                )
                conn.commit()
                flash('Registro actualizado correctamente', 'message')
            except Exception as e:
                flash(f'Error al actualizar registro: {e}', 'error')
                logger.error(f"Error admin_editar_registro (POST) para {username} en {fecha_str}: {e}")
        else:
            flash('Usuario no encontrado', 'error')
        
        cursor.close()
        conn.close()
        return redirect(url_for('admin_usuarios'))
    
    username = request.args.get('usuario')
    fecha_str = request.args.get('fecha')
    registro = None
    
    if username and fecha_str:
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        user_id = cursor.fetchone()
        if user_id:
            cursor.execute(
                "SELECT fecha, inicio, salida, horas_trabajadas, horas_extras FROM registros_asistencia WHERE id_usuario = %s AND fecha = %s",
                (user_id['id'], fecha_str)
            )
            registro_db = cursor.fetchone()
            if registro_db:
                registro = {
                    'fecha': registro_db['fecha'].isoformat(),
                    'inicio': registro_db['inicio'].isoformat() if registro_db['inicio'] else '',
                    'salida': registro_db['salida'].isoformat() if registro_db['salida'] else '',
                    'horas_trabajadas': float(registro_db['horas_trabajadas']),
                    'horas_extras': float(registro_db['horas_extras'])
                }
    
    cursor.close()
    conn.close()

    if registro:
        return render_template('editar_registro.html', usuario=username, fecha=fecha_str, registro=registro)
    
    flash('Registro no encontrado', 'error')
    return redirect(url_for('admin_usuarios'))

# ✅ Gestión de Backups (Admin)
@app.route('/admin/backups')
def admin_backups():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    # En un sistema con DB, los backups se harían a nivel de DB (ej. mysqldump)
    # Por ahora, esta función puede listar backups de DB si se implementan
    # o simplemente indicar que los backups se gestionan a nivel de base de datos.
    
    # Para mantener la funcionalidad de listar archivos JSON de backup si existen
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
    
    flash('Nota: Los backups de datos principales se gestionan a nivel de base de datos MySQL.', 'info')
    return render_template('admin_backups.html', backups=backups_list)

@app.route('/admin/crear_backup')
def admin_crear_backup():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    # Aquí se debería invocar un comando de backup de MySQL, ej:
    # execute_command(f"mysqldump -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} > backups/db_backup_{now_local().strftime('%Y%m%d_%H%M%S')}.sql")
    flash('La funcionalidad de crear backup de la base de datos debe ser implementada (ej. mysqldump).', 'warning')
    return redirect(url_for('admin_backups'))

@app.route('/admin/descargar_backup/<nombre>')
def admin_descargar_backup(nombre):
    if not current_user.is_admin():
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
@csrf.exempt
def seleccionar_turno():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    usuario_id = current_user.id
    username = current_user.username
    cedula = current_user.cedula
    form = EmptyForm()

    if form.validate_on_submit():
        turno_key = request.form.get('turno')  # Formato: "dia_hora" o "fecha_dia_hora"
        fecha_seleccionada_str = request.form.get('fecha_seleccionada') # NUEVO: Recibir fecha del form

        if not turno_key:
            flash('Selecciona un turno válido', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('seleccionar_turno'))
        
        # Determinar la fecha de asignación
        try:
            # Si se proporciona una fecha, usarla. Si no, usar hoy.
            fecha_asignacion = datetime.datetime.strptime(fecha_seleccionada_str, '%Y-%m-%d').date() if fecha_seleccionada_str else today_local_iso()
        except ValueError:
            flash('Formato de fecha inválido. Usa YYYY-MM-DD.', 'error')
            return redirect(url_for('seleccionar_turno'))

        partes_turno = turno_key.split('_')
        dia, hora = partes_turno[0], partes_turno[1]
        
        cursor.execute("SELECT id FROM turnos_disponibles WHERE dia_semana = %s AND hora = %s", (dia, hora))
        turno_disponible_id = cursor.fetchone()
        
        if not turno_disponible_id:
            flash('Turno no válido', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('seleccionar_turno'))
        
        turno_disponible_id = turno_disponible_id['id']

        # Validar que el turno esté disponible (no asignado a otro para hoy)
        cursor.execute(
            "SELECT u.username FROM turnos_asignados ta JOIN usuarios u ON ta.id_usuario = u.id WHERE ta.id_turno_disponible = %s AND ta.fecha_asignacion = %s",
            (turno_disponible_id, fecha_asignacion)
        )
        assigned_user = cursor.fetchone()

        if assigned_user and assigned_user['username'] != username:
            flash('Este turno ya está ocupado por otro usuario', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('seleccionar_turno'))

        # Asignar turno
        try:
            logger.info(f"Inserting turno asignado: id_usuario={usuario_id}, turno_id={turno_disponible_id}, fecha={fecha_asignacion}")
            cursor.execute(
                "INSERT INTO turnos_asignados (id_usuario, id_turno_disponible, fecha_asignacion) VALUES (%s, %s, %s) ON CONFLICT (id_usuario, id_turno_disponible, fecha_asignacion) DO NOTHING",
                (usuario_id, turno_disponible_id, fecha_asignacion)
            )
            conn.commit()
            flash(f'✅ Turno seleccionado para el {fecha_asignacion.strftime("%d/%m/%Y")} exitosamente', 'message')
        except Exception as e:
            flash(f'Error al seleccionar turno: {e}', 'error')
            logger.error(f"Error seleccionar_turno para {username}: {e}")
        
        cursor.close()
        conn.close()
        return redirect(url_for('ver_turnos_asignados'))

    # Para el selector de fecha en el template
    try:
        fecha_para_input = today_local_iso()
    except Exception:
        # Fallback seguro si today_local_iso() falla por alguna razón
        fecha_para_input = datetime.date.today().isoformat()

    # Preparar datos para el template
    shifts = {}
    available_shifts = {}
    
    # PostgreSQL-compatible ordering for days of the week
    order_clause = """
        ORDER BY CASE dia_semana
            WHEN 'monday' THEN 1 WHEN 'tuesday' THEN 2 WHEN 'wednesday' THEN 3
            WHEN 'thursday' THEN 4 WHEN 'friday' THEN 5 WHEN 'saturday' THEN 6 ELSE 7
        END, hora
    """
    cursor.execute(f"SELECT id, dia_semana, hora FROM turnos_disponibles {order_clause}")
    all_shifts_db = cursor.fetchall()

    for s_info in all_shifts_db:
        dia = s_info['dia_semana']
        hora = s_info['hora']
        if dia not in shifts:
            shifts[dia] = {}
            available_shifts[dia] = {}
        
        # Verificar si el turno está asignado para hoy
        cursor.execute(
            "SELECT u.username FROM turnos_asignados ta JOIN usuarios u ON ta.id_usuario = u.id WHERE ta.id_turno_disponible = %s AND ta.fecha_asignacion = %s", # Se podría hacer dinámico con la fecha seleccionada
            (s_info['id'], fecha_para_input)
        )
        assigned_user_data = cursor.fetchone()
        
        shifts[dia][hora] = assigned_user_data['username'] if assigned_user_data else None
        
        # Disponible si no está ocupado por otro usuario
        available_shifts[dia][hora] = (assigned_user_data is None) or (assigned_user_data['username'] == username)

    cursor.close()
    conn.close()

    return render_template('seleccionar_turno.html',
                        shifts=shifts,
                        available_shifts=available_shifts,
                        turnos_usados_usuario={}, # Esto requeriría un historial más complejo en DB
                        fecha_para_input=fecha_para_input, # NUEVO: Pasar fecha para el input
                        form=form,
                        session=session)

# ✅ Ver turnos asignados
@app.route('/ver_turnos_asignados')
def ver_turnos_asignados():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    form = EmptyForm() # Se añade para validación CSRF
    # La validación CSRF es implícita con el formulario, no se necesita un bloque `if` para un GET.
    conn = get_db_connection()
    cursor = conn.cursor()

    
    usuario_id = current_user.id
    admin = current_user.is_admin()
    
    assigned_shifts = {}
    
    # Construir la consulta base
    query = """
        SELECT 
            ta.fecha_asignacion,
            u.username, u.nombre, u.cedula, u.cargo,
            td.dia_semana AS dia, td.hora
        FROM turnos_asignados ta
        JOIN usuarios u ON ta.id_usuario = u.id
        JOIN turnos_disponibles td ON ta.id_turno_disponible = td.id
    """
    params = []

    # Si no es admin, filtrar por su propio ID
    if not admin:
        query += " WHERE ta.id_usuario = %s"
        params.append(usuario_id)

    # Ordenar siempre por fecha (más reciente primero), luego por usuario
    query += " ORDER BY ta.fecha_asignacion DESC, u.username, td.hora"

    cursor.execute(query, tuple(params))
    all_assigned_shifts = cursor.fetchall()
    
    # Agrupar los turnos por fecha
    turnos_por_fecha = {}
    for shift in all_assigned_shifts:
        fecha = shift['fecha_asignacion'].isoformat()
        if fecha not in turnos_por_fecha:
            turnos_por_fecha[fecha] = []
        
        turnos_por_fecha[fecha].append({
            'dia': shift['dia'],
            'hora': shift['hora'],
            'usuario': shift['username'],
            'nombre': shift['nombre'],
            'cedula': shift['cedula'],
            'cargo': shift['cargo']
        })

    cursor.close()
    conn.close()
    
    return render_template('ver_turnos_asignados.html',
                        turnos_por_fecha=turnos_por_fecha,
                        admin=admin,
                        data={'usuarios': {}, 'turnos': {'shifts': {}}}, # Data ya no se carga de JSON
                        session=session)

# ✅ Eliminar turno
@app.route('/eliminar_turno', methods=['POST'])
@csrf.exempt
def eliminar_turno():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    form = EmptyForm() # Se añade para validación CSRF
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        dia = request.form.get('dia')
        hora = request.form.get('hora')
        fecha_str = request.form.get('fecha_asignacion') # Usar un nombre más específico
        # El usuario que se va a eliminar puede ser el actual o uno especificado por el admin
        usuario_a_eliminar = request.form.get('usuario_a_eliminar', current_user.username)
        
        if not dia or not hora:
            flash('Datos de turno inválidos', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('ver_turnos_asignados'))
            
        try:
            fecha_asignacion = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else today_local_iso()
        except ValueError:
            flash('Formato de fecha inválido.', 'error')
            return redirect(url_for('ver_turnos_asignados'))

        # Obtener el ID del usuario cuyo turno se va a eliminar
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (usuario_a_eliminar,))
        user_to_delete_row = cursor.fetchone()
        if not user_to_delete_row:
            flash(f"Usuario '{usuario_a_eliminar}' no encontrado.", 'error')
            return redirect(url_for('ver_turnos_asignados'))

        cursor.execute("SELECT id FROM turnos_disponibles WHERE dia_semana = %s AND hora = %s", (dia, hora))
        turno_disponible_id = cursor.fetchone()
        
        if not turno_disponible_id:
            flash('Turno no encontrado', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('ver_turnos_asignados'))
        
        turno_disponible_id = turno_disponible_id['id']

        # Verificar que el turno pertenece al usuario o es admin
        if usuario_a_eliminar == current_user.username or current_user.is_admin():
            try:
                cursor.execute(
                    "DELETE FROM turnos_asignados WHERE id_usuario = %s AND id_turno_disponible = %s AND fecha_asignacion = %s",
                    (user_to_delete_row['id'], turno_disponible_id, fecha_asignacion)
                )
                if cursor.rowcount > 0:
                    conn.commit()
                    flash('✅ Turno eliminado correctamente y disponible para otros', 'message')
                else:
                    flash('No se encontró el turno asignado para eliminar.', 'warning')

            except Exception as e:
                flash(f'Error al eliminar turno: {e}', 'error')
                logger.error(f"Error eliminar_turno para {usuario_a_eliminar}: {e}")
        else:
            flash('No puedes eliminar este turno', 'error')

        cursor.close()
        conn.close()

    return redirect(url_for('ver_turnos_asignados'))


# ✅ Panel de asignación manual de turnos (Admin)
@app.route('/admin/asignar_turnos')
def admin_asignar_turnos():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    form = EmptyForm() # Se añade para validación CSRF
    # La validación CSRF es implícita con el formulario, no se necesita un bloque `if` para un GET.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener solo gestores (usuarios con cédula en el sistema de turnos)
    cedulas_gestores = ["1070963486", "1067949514", "1140870406", "1068416077"]
    gestores = {}
    
    # Diccionario para traducir los nombres de los días
    dias_nombres = {
        'monday': 'Lunes', 'tuesday': 'Martes', 'wednesday': 'Miércoles',
        'thursday': 'Jueves', 'friday': 'Viernes', 'saturday': 'Sábado',
        'sunday': 'Domingo'
    }

    # Obtener todos los turnos disponibles para los menús desplegables
    cursor.execute("SELECT dia_semana, hora FROM turnos_disponibles ORDER BY hora")
    turnos_disponibles_db = cursor.fetchall()
    turnos_disponibles_por_dia = {}
    for turno in turnos_disponibles_db:
        if turno['dia_semana'] not in turnos_disponibles_por_dia:
            turnos_disponibles_por_dia[turno['dia_semana']] = []
        turnos_disponibles_por_dia[turno['dia_semana']].append(turno['hora'])

    cursor.execute("SELECT id, username, nombre, cedula, cargo FROM usuarios WHERE cedula = ANY(%s)", (cedulas_gestores,))
    gestores_db = cursor.fetchall()

    for usr_info in gestores_db:
        gestores[usr_info['username']] = {
            'id': usr_info['id'],
            'nombre': usr_info['nombre'],
            'cedula': usr_info['cedula'],
            'cargo': usr_info['cargo']
        }

    # Obtener turnos ya asignados para la semana actual
    hoy = now_local().date()
    inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + datetime.timedelta(days=6)

    cursor.execute("""
        SELECT ta.id_usuario, td.dia_semana, td.hora
        FROM turnos_asignados ta
        JOIN turnos_disponibles td ON ta.id_turno_disponible = td.id
        WHERE ta.fecha_asignacion BETWEEN %s AND %s
    """, (inicio_semana, fin_semana))
    
    turnos_asignados_semana = cursor.fetchall()
    
    # Estructurar los turnos asignados por usuario y día
    turnos_por_gestor = {g['id']: {} for g in gestores.values()}
    for turno in turnos_asignados_semana:
        if turno['id_usuario'] in turnos_por_gestor:
            turnos_por_gestor[turno['id_usuario']][turno['dia_semana']] = turno['hora']
    
    cursor.close()
    conn.close()
    
    dias_nombres = {
        'monday': 'Lunes', 'tuesday': 'Martes', 'wednesday': 'Miércoles',
        'thursday': 'Jueves', 'friday': 'Viernes', 'saturday': 'Sábado', 'sunday': 'Domingo'
    }

    return render_template('admin_asignar_turnos.html',
                        turnos_disponibles=turnos_disponibles_por_dia,
                        turnos_asignados=turnos_por_gestor,
                        gestores=gestores,
                        dias_semana=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                        dias_nombres=dias_nombres,
                        form=form)

# ✅ Asignar turno manual (Admin)
@app.route('/admin/asignar_turno_manual', methods=['POST'])
@csrf.exempt
def admin_asignar_turno_manual():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    form = EmptyForm() # Se añade para validación CSRF
    if form.validate_on_submit(): # Se valida el token CSRF
        conn = get_db_connection()
        cursor = conn.cursor()
        
        id_usuario = request.form.get('id_usuario')
        dias_semana = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        hoy = now_local().date()
        inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())

        try:
            # Lógica mejorada para NO borrar historial indiscriminadamente
            # Recorremos cada día de la semana y actualizamos individualmente
            for i, dia_str in enumerate(dias_semana):
                hora = request.form.get(f'turno_{dia_str}')
                fecha_asignacion = inicio_semana + datetime.timedelta(days=i)
                
                if hora: 
                    # 1. Obtener ID del turno disponible
                    cursor.execute("SELECT id FROM turnos_disponibles WHERE dia_semana = %s AND hora = %s", (dia_str, hora))
                    turno_disponible_row = cursor.fetchone()
                    
                    if turno_disponible_row:
                        id_turno_disponible = turno_disponible_row['id']
                        
                        # 2. Insertar el nuevo turno.
                        cursor.execute("""
                            INSERT INTO turnos_asignados (id_usuario, id_turno_disponible, fecha_asignacion) 
                            VALUES (%s, %s, %s)
                            ON CONFLICT (id_usuario, id_turno_disponible, fecha_asignacion) DO NOTHING
                        """, (id_usuario, id_turno_disponible, fecha_asignacion))
                        
                        # Registrar en bitácora
                        registrar_auditoria('Asignación Turno', f"Usuario ID {id_usuario}: Asignado turno {hora} para {fecha_asignacion}")
                        
                        # 3. Limpieza con respaldo: Antes de borrar, guardar en historial si existe
                        cursor.execute("""
                            SELECT id_turno_disponible FROM turnos_asignados 
                            WHERE id_usuario = %s AND fecha_asignacion = %s AND id_turno_disponible != %s
                        """, (id_usuario, fecha_asignacion, id_turno_disponible))
                        turnos_viejos = cursor.fetchall()
                        
                        for tv in turnos_viejos:
                            # Registrar en bitácora el cambio explícito
                            registrar_auditoria('Cambio Turno', f"ID {id_usuario}: Turno ID {tv['id_turno_disponible']} reemplazado por {id_turno_disponible} el {fecha_asignacion}")

                        cursor.execute("""
                            DELETE FROM turnos_asignados 
                            WHERE id_usuario = %s 
                            AND fecha_asignacion = %s 
                            AND id_turno_disponible != %s
                        """, (id_usuario, fecha_asignacion, id_turno_disponible))

                else:
                    # Borrar turno (solo futuros/hoy)
                    # Pero incluso si borramos, ¡REGISTRAMOS LO QUE BORRAMOS!
                    try:
                        hoy_date = now_local().date()
                        if fecha_asignacion >= hoy_date:
                             cursor.execute("""
                                SELECT id_turno_disponible FROM turnos_asignados 
                                WHERE id_usuario = %s AND fecha_asignacion = %s
                            """, (id_usuario, fecha_asignacion))
                             turnos_a_borrar = cursor.fetchall()
                             
                             if turnos_a_borrar:
                                 for tb in turnos_a_borrar:
                                     registrar_auditoria('Eliminación Turno', f"ID {id_usuario}: Eliminado turno ID {tb['id_turno_disponible']} para {fecha_asignacion}")

                             cursor.execute("""
                                DELETE FROM turnos_asignados 
                                WHERE id_usuario = %s 
                                AND fecha_asignacion = %s
                            """, (id_usuario, fecha_asignacion))
                    except Exception as e_inner:
                        logger.error(f"Error en limpieza de turnos: {e_inner}")
            
            conn.commit()
            flash('✅ Turnos actualizados correctamente (Historial protegido)', 'message')
        except Exception as e:
            conn.rollback()
            flash(f'Error al guardar los turnos: {e}', 'error')
            logger.error(f"Error en admin_asignar_turno_manual para usuario {id_usuario}: {e}")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin_asignar_turnos'))

# ✅ Limpiar turno (Admin)
@app.route('/admin/limpiar_turno', methods=['POST'])
def admin_limpiar_turno():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    form = EmptyForm() # Se añade para validación CSRF
    if form.validate_on_submit(): # Se valida el token CSRF
        conn = get_db_connection()
        cursor = conn.cursor()
        
        dia = request.form.get('dia')
        hora = request.form.get('hora')
        
        if dia and hora:
            cursor.execute("SELECT id FROM turnos_disponibles WHERE dia_semana = %s AND hora = %s", (dia, hora))
            turno_disponible_id = cursor.fetchone()
            
            if turno_disponible_id:
                try:
                    cursor.execute(
                        "DELETE FROM turnos_asignados WHERE id_turno_disponible = %s AND fecha_asignacion = %s",
                        (turno_disponible_id['id'], today_local_iso())
                    )
                    conn.commit()
                    flash('✅ Turno liberado', 'message')
                except Exception as e:
                    flash(f'Error al liberar turno: {e}', 'error')
                    logger.error(f"Error admin_limpiar_turno: {e}")
            else:
                flash('Turno no encontrado', 'error')
        
        cursor.close()
        conn.close()
    return redirect(url_for('admin_asignar_turnos'))

# ✅ Panel de edición completa de usuario (Admin)
@app.route('/admin/editar_completo/<username>')
def admin_editar_completo(username):
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    form = EmptyForm()
    # La validación CSRF es implícita con el formulario, no se necesita un bloque `if` para un GET.
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, nombre, cedula, cargo, correo, telefono, admin, bloqueado FROM usuarios WHERE username = %s", (username,))
    usuario_data = cursor.fetchone()
    
    if not usuario_data:
        flash('Usuario no encontrado', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('admin_usuarios'))
    
    cursor.execute(
        "SELECT fecha, inicio, salida, horas_trabajadas, horas_extras FROM registros_asistencia WHERE id_usuario = %s ORDER BY fecha DESC",
        (usuario_data['id'],)
    )
    registros_db = cursor.fetchall()
    
    registros = {}
    for reg in registros_db:
        registros[reg['fecha'].isoformat()] = {
            'inicio': reg['inicio'].isoformat() if reg['inicio'] else None,
            'salida': reg['salida'].isoformat() if reg['salida'] else None,
            'horas_trabajadas': float(reg['horas_trabajadas']),
            'horas_extras': float(reg['horas_extras'])
        }
    
    cursor.close()
    conn.close()
    
    return render_template('admin_editar_completo.html',
                        usuario=username,
                        usuario_data=usuario_data,
                        registros=registros,
                        form=form)

# ✅ Actualizar usuario completo (Admin)
@app.route('/admin/actualizar_usuario_completo', methods=['POST'])
def admin_actualizar_usuario_completo():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    form = EmptyForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        username = request.form.get('usuario')
        
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        user_id = cursor.fetchone()
        
        if user_id:
            nombre = request.form.get('nombre')
            cedula = request.form.get('cedula')
            cargo = request.form.get('cargo')
            correo = request.form.get('correo')
            telefono = request.form.get('telefono', '')
            is_admin = request.form.get('admin') == 'true'
            
            nueva_contrasena = request.form.get('contrasena')
            
            try:
                if nueva_contrasena:
                    hashed_password = generate_password_hash(nueva_contrasena)
                    cursor.execute(
                        "UPDATE usuarios SET nombre = %s, cedula = %s, cargo = %s, correo = %s, telefono = %s, admin = %s, contrasena = %s WHERE id = %s",
                        (nombre, cedula, cargo, correo, telefono, is_admin, hashed_password, user_id['id'])
                    )
                else:
                    cursor.execute(
                        "UPDATE usuarios SET nombre = %s, cedula = %s, cargo = %s, correo = %s, telefono = %s, admin = %s WHERE id = %s",
                        (nombre, cedula, cargo, correo, telefono, is_admin, user_id['id'])
                    )
                conn.commit()
                flash('✅ Usuario actualizado completamente', 'message')
            except Exception as e:
                flash(f'Error al actualizar usuario: {e}', 'error')
                logger.error(f"Error admin_actualizar_usuario_completo para {username}: {e}")
        else:
            flash('Usuario no encontrado', 'error')
        
        cursor.close()
        conn.close()
    return redirect(url_for('admin_usuarios'))

# ✅ Actualizar registro de asistencia (Admin - AJAX)
@app.route('/admin/actualizar_registro', methods=['POST'])
def admin_actualizar_registro():
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': 'Acceso denegado'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    username = request.form.get('usuario')
    fecha_str = request.form.get('fecha')
    inicio_str = request.form.get('inicio')
    salida_str = request.form.get('salida')
    
    cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    user_id = cursor.fetchone()
    
    if user_id:
        try:
            horas_netas = 0.0
            horas_extras = 0.0
            if inicio_str and salida_str:
                horas_netas, horas_extras = calcular_horas(inicio_str, salida_str)
            
            cursor.execute(
                "UPDATE registros_asistencia SET inicio = %s, salida = %s, horas_trabajadas = %s, horas_extras = %s WHERE id_usuario = %s AND fecha = %s",
                (inicio_str, salida_str, horas_netas, horas_extras, user_id['id'], fecha_str)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error admin_actualizar_registro (AJAX) para {username} en {fecha_str}: {e}")
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    cursor.close()
    conn.close()
    return jsonify({'success': False, 'error': 'Registro no encontrado'}), 404

# ✅ Eliminar usuario (Admin)
@app.route('/admin/eliminar_usuario/<usuario>')
def admin_eliminar_usuario(usuario):
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))
    
    if usuario == current_user.username:
        flash('No puedes eliminar tu propio usuario', 'error')
        return redirect(url_for('admin_usuarios'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM usuarios WHERE username = %s", (usuario,))
    user_id = cursor.fetchone()
    
    if user_id:
        try:
            # Eliminar registros de asistencia
            cursor.execute("DELETE FROM registros_asistencia WHERE id_usuario = %s", (user_id['id'],))
            # Eliminar turnos asignados
            cursor.execute("DELETE FROM turnos_asignados WHERE id_usuario = %s", (user_id['id'],))
            # Eliminar tokens de restablecimiento
            cursor.execute("DELETE FROM reset_tokens WHERE id_usuario = %s", (user_id['id'],))
            # Finalmente, eliminar usuario
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id['id'],))
            conn.commit()
            flash(f'✅ Usuario {usuario} eliminado completamente', 'message')
        except Exception as e:
            flash(f'Error al eliminar usuario: {e}', 'error')
            logger.error(f"Error admin_eliminar_usuario para {usuario}: {e}")
    else:
        flash('Usuario no encontrado', 'error')
    
    cursor.close()
    conn.close()
    return redirect(url_for('admin_usuarios'))

# Función auxiliar para validar selección de turno (adaptada para DB)
def validar_turno_usuario(id_usuario, user_role, dia, hora):
    conn = get_db_connection()
    cursor = conn.cursor()

    mes_actual = now_local().strftime('%Y-%m')
    
    # Contar turnos asignados este mes
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM turnos_asignados ta
        WHERE ta.id_usuario = %s AND TO_CHAR(ta.fecha_asignacion, 'YYYY-MM') = %s
    """, (id_usuario, mes_actual))
    turnos_mes = cursor.fetchone()['total']

    # Si ya tiene 4 turnos, no puede seleccionar más hasta próximo mes
    if turnos_mes >= 4:
        cursor.close()
        conn.close()
        return False

    # Verificar que no se repita el turno en el mes (para el día actual)
    cursor.execute("""
        SELECT ta.id
        FROM turnos_asignados ta
        JOIN turnos_disponibles td ON ta.id_turno_disponible = td.id
        WHERE ta.id_usuario = %s AND td.dia_semana = %s AND td.hora = %s AND ta.fecha_asignacion = %s
    """, (id_usuario, dia, hora, today_local_iso()))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False

    # Managers pueden seleccionar cualquier turno disponible
    if user_role == 'manager': # Asumiendo que 'manager' es un cargo
        cursor.close()
        conn.close()
        return True

    # Collaborators tienen restricciones
    # Solo pueden seleccionar turnos de 8:00 en adelante los días de semana
    if dia in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        if hora in ['06:30', '08:00']:
            cursor.close()
            conn.close()
            return False
    
    cursor.close()
    conn.close()
    return True

# ✅ Módulo de Turnos con Trazabilidad
@app.route('/modulo_turnos')
def modulo_turnos():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    semana_param = request.args.get('semana', type=int) or 0
    
    if TZ:
        fecha_base = datetime.datetime(2025, 11, 3, tzinfo=TZ)
        hoy = now_local()
    else:
        fecha_base = datetime.datetime(2025, 11, 3)
        hoy = datetime.datetime.now()
    
    dias_transcurridos = (hoy.date() - fecha_base.date()).days
    semana_actual = (dias_transcurridos // 7) + 1
    if semana_param:
        semana_actual = semana_param if semana_param > 0 else semana_actual
    
    inicio_semana = fecha_base + datetime.timedelta(weeks=semana_actual-1)
    fin_semana = inicio_semana + datetime.timedelta(days=5)

    fechas_semana = []
    for i in range(6):
        fecha = inicio_semana + datetime.timedelta(days=i)
        fechas_semana.append(fecha.strftime('%d/%m/%Y'))
    
    # Obtener turnos de la semana actual
    shifts = {}    
    # Esta consulta obtiene TODOS los turnos disponibles y los une con los asignados para la semana seleccionada.
    cursor.execute("""
        SELECT 
            td.dia_semana, 
            td.hora, 
            asignados.username AS assigned_username
        FROM turnos_disponibles td
        LEFT JOIN (
            SELECT ta.id_turno_disponible, u.username
            FROM turnos_asignados ta
            JOIN usuarios u ON ta.id_usuario = u.id
            WHERE ta.fecha_asignacion BETWEEN %s AND %s
        ) AS asignados ON td.id = asignados.id_turno_disponible
        ORDER BY CASE td.dia_semana WHEN 'monday' THEN 1 WHEN 'tuesday' THEN 2 WHEN 'wednesday' THEN 3 WHEN 'thursday' THEN 4 WHEN 'friday' THEN 5 WHEN 'saturday' THEN 6 ELSE 7 END, td.hora
    """, (inicio_semana.date(), fin_semana.date()))
    current_week_shifts = cursor.fetchall()

    for shift_data in current_week_shifts:
        dia = shift_data['dia_semana']
        hora = shift_data['hora']
        if dia not in shifts:
            shifts[dia] = {}
        shifts[dia][hora] = shift_data['assigned_username']

    historial_turnos = generar_historial_turnos(fecha_base)
    
    # Estadísticas
    cursor.execute("SELECT COUNT(*) AS total FROM turnos_asignados WHERE fecha_asignacion BETWEEN %s AND %s", (inicio_semana.date(), fin_semana.date()))
    total_turnos = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(DISTINCT id_usuario) AS total FROM turnos_asignados WHERE fecha_asignacion BETWEEN %s AND %s", (inicio_semana.date(), fin_semana.date()))
    usuarios_activos = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COUNT(*) AS total FROM turnos_disponibles td
        LEFT JOIN turnos_asignados ta ON td.id = ta.id_turno_disponible AND ta.fecha_asignacion BETWEEN %s AND %s
        WHERE ta.id IS NULL
    """, (inicio_semana.date(), fin_semana.date()))
    turnos_libres = cursor.fetchone()['total']
    
    stats = {
        'total_turnos': total_turnos,
        'usuarios_activos': usuarios_activos,
        'turnos_libres': turnos_libres
    }
    
    usuarios_turnos = obtener_usuarios_con_turnos()
    
    cursor.close()
    conn.close()
    
    return render_template('modulo_turnos.html',
                        semana_actual=semana_actual,
                        fecha_inicio_semana=inicio_semana.strftime('%d/%m/%Y'),
                        fecha_fin_semana=fin_semana.strftime('%d/%m/%Y'),
                        fechas_semana=fechas_semana,
                        turnos_semana=shifts,
                        historial_turnos=historial_turnos,
                        usuarios_turnos=usuarios_turnos,
                        stats=stats,
                        data={'usuarios': {}}) # Data ya no se carga de JSON

def generar_historial_turnos(fecha_base):
    fecha_base = fecha_base.replace(tzinfo=TZ) # Asegurar que la fecha base sea aware
    """Genera historial completo de turnos desde Nov 3, 2025 (adaptado para DB)"""
    historial = []
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Configuración de turnos por cédula
    asignaciones_base = {
        "1070963486": {"turnos": ["06:30", "08:30"]},
        "1067949514": {"turnos": ["08:00", "06:30"]},
        "1140870406": {"turnos": ["08:30", "09:00"]},
        "1068416077": {"turnos": ["09:00", "08:00", "06:30"]}
    }
    
    # Encontrar usuarios por cédula
    cursor.execute("SELECT id, username, nombre, cedula, cargo FROM usuarios WHERE cedula IN (%s, %s, %s, %s)", tuple(asignaciones_base.keys()))
    users_with_cedula = cursor.fetchall()

    for user_info in users_with_cedula:
        cedula = user_info['cedula']
        if cedula in asignaciones_base:
            asignaciones_base[cedula]['id_usuario'] = user_info['id']
            asignaciones_base[cedula]['usuario'] = user_info['username']
            asignaciones_base[cedula]['nombre'] = user_info['nombre']
            asignaciones_base[cedula]['cargo'] = user_info['cargo']
    
    hoy = now_local()
    semanas_transcurridas = ((hoy - fecha_base).days // 7) + 1
    
    for semana in range(1, semanas_transcurridas + 1):
        fecha_inicio = fecha_base + datetime.timedelta(weeks=semana-1)
        
        for cedula, info in asignaciones_base.items():
            if 'id_usuario' in info:
                estado = "Pendiente"
                estado_class = "info"
                
                # Verificar si hay turnos asignados para esta semana
                cursor.execute("""
                    SELECT COUNT(*) AS total FROM turnos_asignados ta
                    JOIN turnos_disponibles td ON ta.id_turno_disponible = td.id
                    WHERE ta.id_usuario = %s AND ta.fecha_asignacion BETWEEN %s AND %s
                """, (info['id_usuario'], fecha_inicio.date(), (fecha_inicio + datetime.timedelta(days=5)).date()))
                turnos_count = cursor.fetchone()['total']

                if turnos_count > 0:
                    if semana < semanas_transcurridas:
                        estado = "Completado"
                        estado_class = "success"
                    elif semana == semanas_transcurridas:
                        estado = "En Curso"
                        estado_class = "warning"
                
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
    
    cursor.close()
    conn.close()
    return sorted(historial, key=lambda x: x['semana'], reverse=True)

def obtener_usuarios_con_turnos():
    """Obtiene información de usuarios con sus patrones de turnos (adaptado para DB)"""
    usuarios_info = []
    
    conn = get_db_connection()
    cursor = conn.cursor()

    patrones_cedula = {
        "1070963486": ["06:30", "08:30"],
        "1067949514": ["08:00", "06:30"],
        "1140870406": ["08:30", "09:00"],
        "1068416077": ["09:00", "08:00", "06:30"]
    }
    
    cursor.execute("SELECT id, username, nombre, cedula, cargo FROM usuarios WHERE cedula IN (%s, %s, %s, %s)", tuple(patrones_cedula.keys()))
    users_with_cedula = cursor.fetchall()

    for user_info in users_with_cedula:
        cedula = user_info['cedula']
        
        # Contar turnos del usuario para hoy
        cursor.execute("""
            SELECT COUNT(*) AS total FROM turnos_asignados ta
            WHERE ta.id_usuario = %s AND ta.fecha_asignacion = %s
        """, (user_info['id'], today_local_iso()))
        total_turnos = cursor.fetchone()['total']
        
        usuarios_info.append({
            'usuario': user_info['username'],
            'nombre': user_info['nombre'],
            'cedula': cedula,
            'cargo': user_info['cargo'],
            'total_turnos': total_turnos,
            'patron': patrones_cedula[cedula]
        })
    
    cursor.close()
    conn.close()
    return usuarios_info

# ✅ NUEVO: Módulo de Turnos Mensual Mejorado
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.values.get('token', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_usuario, expira FROM reset_tokens WHERE token = %s", (token,))
    info_token = cursor.fetchone()

    if not token or not info_token:
        flash('Token inválido o expirado', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('recuperar_contrasena'))

    try:
        expira_dt = info_token['expira']
        if now_local() > expira_dt:
            cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
            conn.commit()
            flash('El token ha expirado. Solicita uno nuevo.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('recuperar_contrasena'))
    except Exception:
        flash('Token inválido', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('recuperar_contrasena'))

    if request.method == 'POST':
        nueva = request.form.get('nueva', '')
        confirmar = request.form.get('confirmar', '')
        if len(nueva) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('reset_password', token=token))
        if nueva != confirmar:
            flash('Las contraseñas no coinciden', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('reset_password', token=token))

        usuario_id = info_token['id_usuario']
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
        if cursor.fetchone():
            try:
                cursor.execute(
                    "UPDATE usuarios SET contrasena = %s WHERE id = %s",
                    (generate_password_hash(nueva), usuario_id)
                )
                cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
                conn.commit()
                flash('✅ Contraseña restablecida correctamente. Ya puedes iniciar sesión.', 'message')
                cursor.close()
                conn.close()
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Error al restablecer contraseña: {e}', 'error')
                logger.error(f"Error reset_password para usuario_id {usuario_id}: {e}")
        else:
            flash('Usuario no encontrado para el token', 'error')
        
        cursor.close()
        conn.close()
        return redirect(url_for('recuperar_contrasena'))

    cursor.close()
    conn.close()
    return render_template('reset_password.html', token=token)

@app.route('/turnos_mensual')
@login_required
def turnos_mensual():
    if not current_user.is_authenticated:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    mes = request.args.get('mes', type=int) or now_local().month
    ano = request.args.get('ano', type=int) or now_local().year
    
    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    patrones_cedula = {
        "1070963486": ["06:30", "08:30"],
        "1067949514": ["08:00", "06:30"],
        "1140870406": ["08:30", "09:00"],
        "1068416077": ["09:00", "08:00", "06:30"]
    }
    
    LIMITE_MENSUAL_TURNOS = 20
    
    gestores_data = []
    cursor.execute("SELECT id, username, nombre, cedula, cargo FROM usuarios WHERE cedula IN (%s, %s, %s, %s)", tuple(patrones_cedula.keys()))
    gestores_db = cursor.fetchall()

    for user_info in gestores_db:
        user_id = user_info['id']
        username = user_info['username']
        cedula = user_info['cedula']

        turnos_usados_mes = []
        cursor.execute("""
            SELECT ta.fecha_asignacion, td.dia_semana, td.hora, ra.inicio, ra.horas_trabajadas
            FROM turnos_asignados ta
            JOIN turnos_disponibles td ON ta.id_turno_disponible = td.id
            LEFT JOIN registros_asistencia ra ON ta.id_usuario = ra.id_usuario AND ta.fecha_asignacion = ra.fecha
            WHERE ta.id_usuario = %s AND EXTRACT(YEAR FROM ta.fecha_asignacion) = %s AND EXTRACT(MONTH FROM ta.fecha_asignacion) = %s
            ORDER BY ta.fecha_asignacion, td.hora
        """, (user_id, ano, mes))
        user_shifts_and_records = cursor.fetchall()

        for record in user_shifts_and_records:
            # Ahora iteramos sobre todos los turnos asignados
            estado = "Pendiente"
            if record['inicio']:
                estado = "Asistió"
            
            turnos_usados_mes.append({
                'fecha': record['fecha_asignacion'].isoformat(),
                'dia': record['dia_semana'],
                'hora': record['hora'],
                'estado': estado,
                'horas_trabajadas': float(record['horas_trabajadas']) if record['horas_trabajadas'] else 0
            })
        
        patron = patrones_cedula[cedula]
        horas_usadas = [t['hora'] for t in turnos_usados_mes]
        turnos_disponibles = [h for h in patron if h not in horas_usadas or horas_usadas.count(h) < 4]
        
        puede_seleccionar = len(turnos_usados_mes) < LIMITE_MENSUAL_TURNOS
        
        gestores_data.append({
            'usuario': username,
            'nombre': user_info['nombre'],
            'cedula': cedula,
            'cargo': user_info['cargo'],
            'patron': patron,
            'turnos_usados': turnos_usados_mes,
            'turnos_disponibles': turnos_disponibles,
            'puede_seleccionar': puede_seleccionar,
            'limite_mensual': LIMITE_MENSUAL_TURNOS
        })
    
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
    
    historial_mes = []
    for gestor in gestores_data:
        for turno in gestor['turnos_usados']:
            estado_class = 'success' if turno['estado'] == 'Asistió' else 'warning'
            historial_mes.append({
                'fecha': turno['fecha'],
                'dia_semana': turno['dia'],
                'gestor': gestor['nombre'],
                'hora': turno['hora'],
                'estado': turno['estado'],
                'estado_class': estado_class,
                'horas_trabajadas': turno['horas_trabajadas']
            })
    
    historial_mes.sort(key=lambda x: x['fecha'], reverse=True)
    
    cursor.close()
    conn.close()
    
    return render_template('turnos_mensual.html',
                        mes_nombre=meses_nombres[mes],
                        ano_actual=ano,
                        mes_actual=mes,
                        gestores_data=gestores_data,
                        stats=stats,
                        historial_mes=historial_mes,
                        session=session)

# ✅ NUEVA RUTA: Importar Turnos Históricos (Admin)
@app.route('/admin/importar_turnos_historicos')
@login_required
def importar_turnos_historicos():
    if not current_user.is_admin():
        flash('Acceso denegado', 'error')
        return redirect(url_for('home'))

    # Datos históricos proporcionados por el usuario
    raw_shift_data = {
        "NATALIA AREVALO": {"cedula": "1070963486", "shifts": [
            ("5/11/2025", "6:30 a.m."), ("6/11/2025", "6:30 a.m."), ("7/11/2025", "6:30 a.m."),
            ("8/11/2025", "8:30 a.m."), ("9/11/2025", "8:30 a.m."), ("10/11/2025", "8:30 a.m."),
            ("11/11/2025", "8:30 a.m."), ("12/11/2025", "8:30 a.m."), ("13/11/2025", "8:30 a.m."),
            ("14/11/2025", "8:30 a.m."), ("15/11/2025", "11:30 a.m."), ("18/11/2025", "9:00 a.m.")
        ]},
        "LESLY GUZMAN": {"cedula": "1067949514", "shifts": [
            ("5/11/2025", "8:00 a.m."), ("6/11/2025", "8:00 a.m."), ("7/11/2025", "8:00 a.m."),
            ("8/11/2025", "6:30 a.m."), ("9/11/2025", "6:30 a.m."), ("10/11/2025", "6:30 a.m."),
            ("11/11/2025", "6:30 a.m."), ("12/11/2025", "6:30 a.m."), ("13/11/2025", "6:30 a.m."),
            ("14/11/2025", "6:30 a.m."), ("15/11/2025", "11:00 a.m."), ("18/11/2025", "8:30 a.m.")
        ]},
        "PAOLA GARCIA": {"cedula": "1140870406", "shifts": [
            ("5/11/2025", "8:30 a.m."), ("6/11/2025", "8:30 a.m."), ("7/11/2025", "8:30 a.m."),
            ("8/11/2025", "9:00 a.m."), ("9/11/2025", "9:00 a.m."), ("10/11/2025", "9:00 a.m."),
            ("11/11/2025", "9:00 a.m."), ("12/11/2025", "9:00 a.m."), ("13/11/2025", "9:00 a.m."),
            ("14/11/2025", "9:00 a.m."), ("15/11/2025", "10:00 a.m."), ("18/11/2025", "8:00 a.m.")
        ]},
        "DAYANA GONZALEZ": {"cedula": "1068416077", "shifts": [
            ("5/11/2025", "9:00 a.m."), ("6/11/2025", "9:00 a.m."), ("7/11/2025", "9:00 a.m."),
            ("8/11/2025", "8:00 a.m."), ("9/11/2025", "8:00 a.m."), ("10/11/2025", "8:00 a.m."),
            ("11/11/2025", "8:00 a.m."), ("12/11/2025", "8:00 a.m."), ("13/11/2025", "8:00 a.m."),
            ("14/11/2025", "8:00 a.m."), ("15/11/2025", "7:00 a.m."), ("18/11/2025", "6:30 a.m.")
        ]}
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    imported_count = 0
    skipped_count = 0
    error_messages = []

    for user_name, user_data in raw_shift_data.items():
        cedula = user_data["cedula"]
        
        cursor.execute("SELECT id FROM usuarios WHERE cedula = %s", (cedula,))
        user_id_row = cursor.fetchone()

        if not user_id_row:
            error_messages.append(f"Usuario con cédula {cedula} ({user_name}) no encontrado. Saltando sus turnos.")
            skipped_count += len(user_data["shifts"])
            continue
        
        id_usuario = user_id_row['id']

        for date_str, time_str_am_pm in user_data["shifts"]:
            try:
                # Parsear fecha (ej. "5/11/2025" a datetime.date)
                day, month, year = map(int, date_str.split('/'))
                fecha_asignacion = datetime.date(year, month, day)
                dia_semana = fecha_asignacion.strftime('%A').lower() # ej. 'wednesday'

                # Parsear hora (ej. "6:30 a.m." a "06:30")
                hora_24h = parse_time_am_pm(time_str_am_pm)
                if not hora_24h:
                    error_messages.append(f"Hora inválida '{time_str_am_pm}' para {user_name} en {date_str}. Saltando.")
                    skipped_count += 1
                    continue

                # Obtener id_turno_disponible
                cursor.execute("SELECT id FROM turnos_disponibles WHERE dia_semana = %s AND hora = %s", (dia_semana, hora_24h))
                turno_disponible_id_row = cursor.fetchone()

                if not turno_disponible_id_row:
                    error_messages.append(f"Turno disponible '{dia_semana} {hora_24h}' no encontrado en la base de datos para {user_name} en {date_str}. Asegúrate de que init_db() se ejecutó correctamente. Saltando.")
                    skipped_count += 1
                    continue
                
                id_turno_disponible = turno_disponible_id_row['id']

                # Insertar en turnos_asignados (ON CONFLICT DO NOTHING para evitar duplicados)
                cursor.execute(
                    "INSERT INTO turnos_asignados (id_usuario, id_turno_disponible, fecha_asignacion) VALUES (%s, %s, %s) ON CONFLICT (id_usuario, id_turno_disponible, fecha_asignacion) DO NOTHING",
                    (id_usuario, id_turno_disponible, fecha_asignacion)
                )
                if cursor.rowcount > 0:
                    imported_count += 1
                else:
                    # Si el turno ya existía, también contamos como "saltado" en la importación de asistencia
                    skipped_count += 1

                # ✅ AÑADIR REGISTRO DE ASISTENCIA CON LA HORA DE INICIO
                # Construir el objeto datetime para el inicio
                h, m = map(int, hora_24h.split(':'))
                inicio_dt = datetime.datetime(year, month, day, h, m)
                # Asegurarse de que tenga la zona horaria correcta
                inicio_dt_tz = TZ.localize(inicio_dt) if TZ and hasattr(TZ, 'localize') else inicio_dt

                # Insertar en registros_asistencia, si no existe ya un registro para ese día
                logger.info(f"Inserting registro asistencia historico: id_usuario={id_usuario}, fecha={fecha_asignacion}")
                cursor.execute(
                    "INSERT INTO registros_asistencia (id_usuario, fecha, inicio) VALUES (%s, %s, %s) ON CONFLICT (id_usuario, fecha) DO NOTHING",
                    (id_usuario, fecha_asignacion, inicio_dt_tz.isoformat())
                )
                # No necesitamos contar esto por separado, el conteo de turnos es suficiente

            except Exception as e:
                error_messages.append(f"Error procesando turno para {user_name} en {date_str} {time_str_am_pm}: {e}. Saltando.")
                logger.error(f"Error importando turno histórico: {e}")
                skipped_count += 1

    conn.commit()
    cursor.close()
    conn.close()

    if imported_count > 0:
        flash(f"✅ Se importaron y registraron {imported_count} turnos históricos exitosamente.", 'message')
    if skipped_count > 0:
        flash(f"⚠️ Se saltaron {skipped_count} turnos (ya existían o hubo errores).", 'warning')
    for msg in error_messages:
        flash(msg, 'error')

    return redirect(url_for('admin_usuarios')) # Redirigir a la GESTIÓN DE USUARIOS para ver los registros

# -------------------
# Ejecutar aplicación
# -------------------
# Inicializar la base de datos al iniciar la aplicación
init_db()

# Advertencia si se usa SECRET_KEY por defecto
if app.secret_key.startswith('CHANGE_THIS'):
    logger.warning("ADVERTENCIA: Usando SECRET_KEY por defecto. Configura una en .env para produccion!")

if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_DEBUG') == '1')

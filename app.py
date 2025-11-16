from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import json
import datetime
import os
import csv
import io
import shutil

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_para_sesiones')

# Función de backup manual (sin scheduler automático)
def backup_automatico():
    """Crea backup manual del archivo de datos"""
    try:
        fecha = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
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
# Funciones de carga y guardado
# -------------------
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'usuarios': {
            'LuisMolina': {
                'contrasena': 'Mathiasmc',
                'admin': True,
                'nombre': 'Luis Molina',
                'cedula': '',
                'cargo': 'Coordinador',
                'correo': 'lemolina0323@gmail.com',
                'role': 'manager'
            }
        },
        'turnos': {
            'shifts': {
                'monday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'tuesday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'wednesday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'thursday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'friday': {'06:30': None, '08:00': None, '08:30': None, '09:00': None},
                'saturday': {'08:00': None}
            },
            'monthly_assignments': {},
            'current_month': datetime.datetime.now().strftime('%Y-%m')
        },
        'registros': {}
    }

def guardar_datos(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

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

# ✅ LOGIN unificado
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        data = cargar_datos()

        if usuario in data['usuarios']:
            if data['usuarios'][usuario].get('bloqueado', False):
                flash('Tu cuenta está bloqueada. Contacta al administrador.', 'error')
                return redirect(url_for('login'))
            
            if data['usuarios'][usuario]['contrasena'] == contrasena:
                session['usuario'] = usuario
                session['nombre'] = data['usuarios'][usuario]['nombre']
                session['admin'] = data['usuarios'][usuario].get('admin', False)
                flash(f'Bienvenido {session["nombre"]}', 'message')
                return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Función para asignar turnos automáticamente basado en cédula
def asignar_turnos_automaticos(data, cedula, usuario):
    shift_assignments = {
        "1070963486": ["06:30", "08:30"],
        "1067949514": ["08:00", "06:30"],
        "1140870406": ["08:30", "09:00"],
        "1068416077": ["09:00", "08:00"]
    }

    if cedula not in shift_assignments:
        return  # No asignar si no está en la lista

    shifts = shift_assignments[cedula]
    current_month = data['turnos']['current_month']
    monthly_assignments = data['turnos']['monthly_assignments']

    # Marcar turnos usados la semana pasada (desde Nov 3, 2025)
    fecha_inicio = datetime.datetime(2025, 11, 3)
    hoy = datetime.datetime.now()
    dias_semana = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

    # Asignar turnos empezando con 6:30 esta semana
    assigned_count = 0
    for dia in dias_semana:
        if assigned_count >= 4:  # Máximo 4 turnos por mes
            break
        for hora in shifts:
            if hora in data['turnos']['shifts'][dia] and data['turnos']['shifts'][dia][hora] is None:
                # Verificar que no se repita en el mes
                turno_key = f"{dia}_{hora}"
                if turno_key not in monthly_assignments.get(usuario, []):
                    data['turnos']['shifts'][dia][hora] = usuario
                    if usuario not in monthly_assignments:
                        monthly_assignments[usuario] = []
                    monthly_assignments[usuario].append(turno_key)
                    assigned_count += 1
                    break

# ✅ Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        cargo = request.form['cargo']
        correo = request.form['correo']
        telefono = request.form.get('telefono', '')
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        data = cargar_datos()
        if usuario not in data['usuarios']:
            data['usuarios'][usuario] = {
                'nombre': nombre,
                'cedula': cedula,
                'cargo': cargo,
                'correo': correo,
                'telefono': telefono,
                'contrasena': contrasena,
                'admin': False
            }
            # Asignar turnos automáticamente si la cédula está en la lista
            asignar_turnos_automaticos(data, cedula, usuario)
            guardar_datos(data)
            flash('Usuario registrado con éxito. Turnos asignados automáticamente si aplica.', 'message')
            return redirect(url_for('login'))
        else:
            flash('El usuario ya existe.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

# ✅ Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'message')
    return redirect(url_for('home'))

# ✅ Dashboard - Usuarios normales ven solo su info, admins ven todo
@app.route('/dashboard')
def dashboard():
     if 'usuario' not in session:
         flash('Debes iniciar sesión primero', 'error')
         return redirect(url_for('login'))

     data = cargar_datos()
     admin = session.get('admin', False)
     
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
         costo_horas_extras = {usuario_actual: costo_horas_extras.get(usuario_actual, 0)}
         costo_total_empresa = costo_horas_extras.get(usuario_actual, 0)
         total_usuarios_nuevos = 1  # Solo mostrar 1 para el usuario actual

     return render_template(
         'dashboard.html',
         registros=registros_limpios,
         admin=admin,
         nombre=session['nombre'],
         year=year,
         fechas=fechas_ordenadas,
         horas_fechas=horas_fechas,
         usuarios_iniciados_hoy=usuarios_iniciados_hoy,
         contador_inicios=contador_inicios,
         total_usuarios_nuevos=total_usuarios_nuevos,
         costo_horas_extras=costo_horas_extras,
         costo_total_empresa=costo_total_empresa,
         valor_hora_ordinaria=round(valor_hora_ordinaria, 2)
     )

# ✅ Marcar inicio
@app.route('/marcar_inicio', methods=['POST'])
def marcar_inicio():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    hoy = datetime.date.today().isoformat()
    ahora = datetime.datetime.now().isoformat()

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

# ✅ Marcar salida
@app.route('/marcar_salida', methods=['POST'])
def marcar_salida():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    hoy = datetime.date.today().isoformat()
    ahora = datetime.datetime.now()

    if usuario in data['registros'] and hoy in data['registros'][usuario] and data['registros'][usuario][hoy]['inicio']:
        inicio = datetime.datetime.fromisoformat(data['registros'][usuario][hoy]['inicio'])
        horas_trabajadas = (ahora - inicio).total_seconds() / 3600
        horas_extras = max(0, horas_trabajadas - 8 if ahora.weekday() < 5 else horas_trabajadas - 4)

        data['registros'][usuario][hoy]['salida'] = ahora.isoformat()
        data['registros'][usuario][hoy]['horas_trabajadas'] = round(horas_trabajadas, 2)
        data['registros'][usuario][hoy]['horas_extras'] = round(horas_extras, 2)
        guardar_datos(data)

        flash(f'Salida registrada. Horas: {round(horas_trabajadas,2)}h, Extras: {round(horas_extras,2)}h', 'message')
    else:
        flash('No hay registro de inicio.', 'error')

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

# ✅ Cambiar contraseña
@app.route('/cambiar_contrasena', methods=['POST'])
def cambiar_contrasena():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']

    actual = request.form.get('actual')
    nueva = request.form.get('nueva')

    if usuario in data['usuarios'] and data['usuarios'][usuario]['contrasena'] == actual:
        data['usuarios'][usuario]['contrasena'] = nueva
        guardar_datos(data)
        flash('Contraseña actualizada correctamente', 'message')
    else:
        flash('La contraseña actual no es correcta', 'error')

    return redirect(url_for('ajustes'))

# ✅ Recuperar contraseña (genera nueva contraseña y envía notificación)
@app.route('/recuperar_contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        correo = request.form.get('correo')
        data = cargar_datos()
        for usr, info in data['usuarios'].items():
            if info.get('correo') == correo:
                # Generar nueva contraseña aleatoria
                import random
                import string
                nueva_contrasena = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                data['usuarios'][usr]['contrasena'] = nueva_contrasena
                guardar_datos(data)

                # Enviar notificación por email (mailto)
                import urllib.parse
                asunto = urllib.parse.quote("Recuperación de Contraseña - Sistema Empleados")
                cuerpo = urllib.parse.quote(f"Hola {info.get('nombre', usr)},\n\nTu nueva contraseña es: {nueva_contrasena}\n\nPor favor, cámbiala después de iniciar sesión.\n\nSaludos,\nSistema de Empleados")
                mailto_link = f"mailto:{correo}?subject={asunto}&body={cuerpo}"

                # Generar enlace de WhatsApp si hay número
                whatsapp_link = ""
                telefono = info.get('telefono', info.get('whatsapp', ''))
                if telefono:
                    telefono = telefono.replace('+', '').replace('-', '').replace(' ', '')
                    whatsapp_msg = urllib.parse.quote(f"🔐 *Recuperación de Contraseña*\n\nHola {info.get('nombre', usr)},\n\nTu nueva contraseña es: *{nueva_contrasena}*\n\nPor favor, cámbiala después de iniciar sesión.\n\n_Sistema de Empleados_")
                    whatsapp_link = f"https://wa.me/{telefono}?text={whatsapp_msg}"

                mensaje = f'✅ Nueva contraseña generada: {nueva_contrasena}<br><a href="{mailto_link}" target="_blank" style="color:#fff;text-decoration:underline;">📧 Enviar por Email</a>'
                if whatsapp_link:
                    mensaje += f' | <a href="{whatsapp_link}" target="_blank" style="color:#fff;text-decoration:underline;">📱 Enviar por WhatsApp</a>'
                
                flash(mensaje, 'message')
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
             data['usuarios'][usuario]['contrasena'] = nueva_clave
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

# ✅ Eliminar usuario (Admin)
@app.route('/admin/eliminar_usuario', methods=['POST'])
def admin_eliminar_usuario():
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     usuario = request.form.get('usuario')
     
     if not usuario:
         flash('Usuario no especificado', 'error')
         return redirect(url_for('admin_usuarios'))
     
     if usuario == session['usuario']:
         flash('No puedes eliminar tu propia cuenta', 'error')
         return redirect(url_for('admin_usuarios'))
     
     data = cargar_datos()
     
     if usuario in data['usuarios']:
         del data['usuarios'][usuario]
         if usuario in data['registros']:
             del data['registros'][usuario]
         guardar_datos(data)
         flash(f'Usuario {usuario} eliminado completamente', 'message')
     else:
         flash('Usuario no encontrado', 'error')
     
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
                 inicio_dt = datetime.datetime.fromisoformat(inicio)
                 salida_dt = datetime.datetime.fromisoformat(salida)
                 horas_trabajadas = (salida_dt - inicio_dt).total_seconds() / 3600
                 horas_extras = max(0, horas_trabajadas - 8 if inicio_dt.weekday() < 5 else horas_trabajadas - 4)
                 
                 data['registros'][usuario][fecha]['horas_trabajadas'] = round(horas_trabajadas, 2)
                 data['registros'][usuario][fecha]['horas_extras'] = round(horas_extras, 2)
             
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
    user_role = data['usuarios'][usuario].get('role', 'collaborator')
    current_month = data['turnos']['current_month']

    if request.method == 'POST':
        dia = request.form.get('dia')
        hora = request.form.get('hora')

        if not dia or not hora:
            flash('Selecciona un día y hora válidos', 'error')
            return redirect(url_for('seleccionar_turno'))

        # Validar que el turno esté disponible
        if data['turnos']['shifts'][dia][hora] is not None:
            flash('Este turno ya está ocupado', 'error')
            return redirect(url_for('seleccionar_turno'))

        # Validar restricciones de rol y ciclo mensual
        if not validar_turno_usuario(data, usuario, user_role, dia, hora):
            flash('No puedes seleccionar este turno según las reglas', 'error')
            return redirect(url_for('seleccionar_turno'))

        # Asignar turno
        data['turnos']['shifts'][dia][hora] = usuario

        # Registrar asignación mensual
        if usuario not in data['turnos']['monthly_assignments']:
            data['turnos']['monthly_assignments'][usuario] = []
        data['turnos']['monthly_assignments'][usuario].append(f"{dia}_{hora}")

        guardar_datos(data)
        flash('Turno seleccionado exitosamente', 'message')
        return redirect(url_for('ver_turnos_asignados'))

    # Preparar datos para el template
    shifts = data['turnos']['shifts']
    available_shifts = {}

    for dia, horas in shifts.items():
        available_shifts[dia] = {}
        for hora, assigned_user in horas.items():
            if assigned_user is None:
                # Verificar si el usuario puede seleccionar este turno
                if validar_turno_usuario(data, usuario, user_role, dia, hora):
                    available_shifts[dia][hora] = True
                else:
                    available_shifts[dia][hora] = False
            else:
                available_shifts[dia][hora] = False

    return render_template('seleccionar_turno.html',
                         shifts=shifts,
                         available_shifts=available_shifts,
                         user_role=user_role)

# ✅ Ver turnos asignados
@app.route('/ver_turnos_asignados')
def ver_turnos_asignados():
    if 'usuario' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('login'))

    data = cargar_datos()
    usuario = session['usuario']
    admin = session.get('admin', False)

    if admin:
        # Mostrar todos los turnos asignados
        assigned_shifts = {}
        for dia, horas in data['turnos']['shifts'].items():
            for hora, assigned_user in horas.items():
                if assigned_user:
                    if assigned_user not in assigned_shifts:
                        assigned_shifts[assigned_user] = []
                    assigned_shifts[assigned_user].append({
                        'dia': dia,
                        'hora': hora,
                        'usuario': assigned_user,
                        'nombre': data['usuarios'].get(assigned_user, {}).get('nombre', assigned_user)
                    })
    else:
        # Mostrar solo turnos del usuario actual
        assigned_shifts = {usuario: []}
        for dia, horas in data['turnos']['shifts'].items():
            for hora, assigned_user in horas.items():
                if assigned_user == usuario:
                    assigned_shifts[usuario].append({
                        'dia': dia,
                        'hora': hora,
                        'usuario': usuario,
                        'nombre': data['usuarios'][usuario]['nombre']
                    })

    return render_template('ver_turnos_asignados.html',
                         assigned_shifts=assigned_shifts,
                         admin=admin)

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
    
    for usuario, info in data['usuarios'].items():
        cedula = info.get('cedula', '')
        if cedula in patrones_cedula:
            # Contar turnos del usuario
            total_turnos = sum(1 for dia in data['turnos']['shifts'].values() 
                             for usr in dia.values() if usr == usuario)
            
            usuarios_info.append({
                'nombre': info.get('nombre', usuario),
                'cedula': cedula,
                'cargo': info.get('cargo', 'N/A'),
                'total_turnos': total_turnos,
                'patron': patrones_cedula[cedula]
            })
    
    return usuarios_info

# -------------------
# Ejecutar aplicación
# -------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

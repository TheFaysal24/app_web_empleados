from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import json
import datetime
import os
import csv
import io
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_para_sesiones')

# Inicializar scheduler para backups automáticos
scheduler = BackgroundScheduler()

def backup_automatico():
    """Crea backup automático del archivo de datos"""
    try:
        fecha = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        if os.path.exists(DATA_FILE):
            import shutil
            backup_file = f'backups/empleados_data_backup_{fecha}.json'
            shutil.copy2(DATA_FILE, backup_file)
            print(f"✅ Backup automático creado: {backup_file}")
            
            # Limpiar backups antiguos (mantener solo los últimos 10)
            archivos = sorted([f for f in os.listdir('backups') if f.endswith('.json')])
            if len(archivos) > 10:
                for archivo in archivos[:-10]:
                    os.remove(os.path.join('backups', archivo))
    except Exception as e:
        print(f"❌ Error en backup automático: {e}")

# Programar backup cada 10 días
scheduler.add_job(func=backup_automatico, trigger="interval", days=10, id='backup_job')
scheduler.start()

# Apagar el scheduler cuando la app se cierre
atexit.register(lambda: scheduler.shutdown())

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
                'correo': 'lemolina0323@gmail.com'
            }
        },
        'turnos': [],
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

# ✅ Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        cargo = request.form['cargo']
        correo = request.form['correo']
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        data = cargar_datos()
        if usuario not in data['usuarios']:
            data['usuarios'][usuario] = {
                'nombre': nombre,
                'cedula': cedula,
                'cargo': cargo,
                'correo': correo,
                'contrasena': contrasena,
                'admin': False
            }
            guardar_datos(data)
            flash('Usuario registrado con éxito.', 'message')
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

     empleados_horas = {}
     fechas_horas = {}
     for usr, info in data['usuarios'].items():
         total_horas = 0
         for fecha, reg in data['registros'].get(usr, {}).items():
             if isinstance(reg, dict):
                 total_horas += reg.get('horas_trabajadas', 0)
                 if fecha not in fechas_horas:
                     fechas_horas[fecha] = 0
                 fechas_horas[fecha] += reg.get('horas_trabajadas', 0)
         empleados_horas[info['nombre']] = total_horas

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

     return render_template(
         'dashboard.html',
         registros=registros_limpios,
         admin=admin,
         nombre=session['nombre'],
         year=year,
         empleados_horas=empleados_horas,
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

    if usuario in data['usuarios']:
        if nombre: data['usuarios'][usuario]['nombre'] = nombre
        if cargo: data['usuarios'][usuario]['cargo'] = cargo
        if correo: data['usuarios'][usuario]['correo'] = correo
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

# ✅ Recuperar contraseña (flujo simple)
@app.route('/recuperar_contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        correo = request.form.get('correo')
        data = cargar_datos()
        for usr, info in data['usuarios'].items():
            if info['correo'] == correo:
                flash(f'Se envió un enlace de recuperación a {correo}', 'message')
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
@app.route('/admin/cambiar_clave/<usuario>', methods=['GET', 'POST'])
def admin_cambiar_clave(usuario):
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     data = cargar_datos()
     
     if request.method == 'POST':
         nueva_clave = request.form.get('nueva_clave')
         
         if usuario in data['usuarios'] and nueva_clave:
             data['usuarios'][usuario]['contrasena'] = nueva_clave
             guardar_datos(data)
             flash(f'Contraseña actualizada para {usuario}', 'message')
         else:
             flash('Error al actualizar contraseña', 'error')
         
         return redirect(url_for('admin_usuarios'))
     
     if usuario in data['usuarios']:
         return render_template('admin_cambiar_clave.html', usuario=usuario, datos=data['usuarios'][usuario])
     
     flash('Usuario no encontrado', 'error')
     return redirect(url_for('admin_usuarios'))

# ✅ Desbloquear usuario (Admin)
@app.route('/admin/desbloquear/<usuario>', methods=['POST'])
def admin_desbloquear(usuario):
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     data = cargar_datos()
     
     if usuario in data['usuarios']:
         data['usuarios'][usuario]['bloqueado'] = False
         guardar_datos(data)
         flash(f'Usuario {usuario} desbloqueado', 'message')
     else:
         flash('Usuario no encontrado', 'error')
     
     return redirect(url_for('admin_usuarios'))

# ✅ Bloquear usuario (Admin)
@app.route('/admin/bloquear/<usuario>', methods=['POST'])
def admin_bloquear(usuario):
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
     data = cargar_datos()
     
     if usuario in data['usuarios']:
         data['usuarios'][usuario]['bloqueado'] = True
         guardar_datos(data)
         flash(f'Usuario {usuario} bloqueado', 'message')
     else:
         flash('Usuario no encontrado', 'error')
     
     return redirect(url_for('admin_usuarios'))

# ✅ Eliminar registro (Admin)
@app.route('/admin/eliminar_registro/<usuario>/<fecha>', methods=['POST'])
def admin_eliminar_registro(usuario, fecha):
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('dashboard'))
     
     data = cargar_datos()
     
     if usuario in data['registros'] and fecha in data['registros'][usuario]:
         del data['registros'][usuario][fecha]
         guardar_datos(data)
         flash(f'Registro del {fecha} eliminado para {usuario}', 'message')
     else:
         flash('Registro no encontrado', 'error')
     
     return redirect(url_for('admin_usuarios'))

# ✅ Eliminar usuario (Admin)
@app.route('/admin/eliminar_usuario/<usuario>', methods=['POST'])
def admin_eliminar_usuario(usuario):
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('home'))
     
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
@app.route('/admin/editar_registro/<usuario>/<fecha>', methods=['GET', 'POST'])
def admin_editar_registro(usuario, fecha):
     if 'usuario' not in session or not session.get('admin'):
         flash('Acceso denegado', 'error')
         return redirect(url_for('dashboard'))
     
     data = cargar_datos()
     
     if request.method == 'POST':
         inicio = request.form.get('inicio')
         salida = request.form.get('salida')
         
         if usuario in data['registros'] and fecha in data['registros'][usuario]:
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
             return redirect(url_for('dashboard'))
     
     if usuario in data['registros'] and fecha in data['registros'][usuario]:
         registro = data['registros'][usuario][fecha]
         return render_template('editar_registro.html', usuario=usuario, fecha=fecha, registro=registro)
     
     flash('Registro no encontrado', 'error')
     return redirect(url_for('dashboard'))

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

# -------------------
# Ejecutar aplicación
# -------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
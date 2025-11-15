from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import json
import datetime
import os
import csv
import io

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

DATA_FILE = 'empleados_data.json'

# ---------------------- Funciones de carga y guardado ----------------------
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'usuarios': {
            'admin': {
                'contrasena': '1234',
                'admin': True,
                'nombre': 'Administrador',
                'cedula': '',
                'cargo': 'Admin',
                'correo': 'admin@empresa.com'
            }
        },
        'turnos': [],
        'registros': {}
    }

def guardar_datos(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# ---------------------- Context processor para fecha y hora ----------------------
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

# ---------------------- Rutas principales ----------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']
    data = cargar_datos()
    if usuario in data['usuarios'] and data['usuarios'][usuario]['contrasena'] == contrasena:
        session['usuario'] = usuario
        session['nombre'] = data['usuarios'][usuario]['nombre']
        session['admin'] = data['usuarios'][usuario].get('admin', False)
        flash(f'Bienvenido {session["nombre"]}')
        return redirect(url_for('dashboard'))
    flash('Usuario o contraseña incorrectos')
    return redirect(url_for('login_page'))

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
            flash('Usuario registrado con éxito. Ya puedes iniciar sesión.')
            return redirect(url_for('login_page'))
        else:
            flash('El usuario ya existe.')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada')
    return redirect(url_for('home'))

# ---------------------- Dashboard con datos para gráficos ----------------------
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login_page'))

    data = cargar_datos()
    usuario = session['usuario']
    registros_usuario = data['registros'].get(usuario, {})

    # Limpiamos datos incorrectos
    registros_limpios = {}
    for key, value in registros_usuario.items():
        if isinstance(value, dict) and 'inicio' in value:
            registros_limpios[key] = value

    # Pasamos el año actual
    year = datetime.datetime.now().year

    # Datos para gráficos
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

    # Ordenar fechas para gráfico de líneas (últimos 7 días)
    fechas_ordenadas = sorted(fechas_horas.keys())[-7:]
    horas_fechas = [fechas_horas[fecha] for fecha in fechas_ordenadas]

    return render_template(
        'dashboard.html',
        registros=registros_limpios,
        admin=session.get('admin', False),
        nombre=session['nombre'],
        year=year,
        empleados_horas=empleados_horas,
        fechas=fechas_ordenadas,
        horas_fechas=horas_fechas
    )

# ---------------------- Marcar inicio ----------------------
@app.route('/marcar_inicio', methods=['POST'])
def marcar_inicio():
    if 'usuario' not in session:
        return redirect(url_for('login_page'))

    data = cargar_datos()
    usuario = session['usuario']
    hoy = datetime.date.today().isoformat()
    ahora = datetime.datetime.now().isoformat()

    if usuario not in data['registros']:
        data['registros'][usuario] = {}

    data['registros'][usuario][hoy] = {
        'inicio': ahora,
        'salida': None,
        'horas_trabajadas': 0,
        'horas_extras': 0
    }

    guardar_datos(data)
    flash(f'Hora de inicio registrada: {ahora}')
    return redirect(url_for('dashboard'))

# ---------------------- Marcar salida ----------------------
@app.route('/marcar_salida', methods=['POST'])
def marcar_salida():
    if 'usuario' not in session:
        return redirect(url_for('login_page'))

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

        flash(f'Salida registrada. Horas trabajadas: {round(horas_trabajadas,2)}h, Extras: {round(horas_extras,2)}h')
    else:
        flash('No hay registro de inicio para hoy.')

    return redirect(url_for('dashboard'))

# ---------------------- Exportar datos ----------------------
@app.route('/exportar_datos')
def exportar_datos():
    if not session.get('admin'):
        flash('Acceso denegado')
        return redirect(url_for('dashboard'))

    data = cargar_datos()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Usuario','Nombre','Cédula','Cargo','Correo','Fecha','Inicio','Salida','Horas Trabajadas','Horas Extras'])

    for usuario, info in data['usuarios'].items():
        registros = data['registros'].get(usuario, {})
        for fecha, reg in registros.items():
            if isinstance(reg, dict):
                writer.writerow([
                    usuario, info['nombre'], info['cedula'], info['cargo'], info['correo'],
                    fecha, reg.get('inicio',''), reg.get('salida',''),
                    reg.get('horas_trabajadas',0), reg.get('horas_extras',0)
                ])

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv', as_attachment=True,
                     download_name='datos_empleados.csv')

# ---------------------- Ejecutar app (MODIFICADO PARA PRODUCCIÓN) ----------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
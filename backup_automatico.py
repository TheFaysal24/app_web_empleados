import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import datetime
import shutil

def crear_backup():
    """Crea un backup del archivo de datos"""
    fecha = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Crear carpeta de backups si no existe
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    # Copiar archivo de datos
    if os.path.exists('empleados_data.json'):
        backup_file = f'backups/empleados_data_backup_{fecha}.json'
        shutil.copy2('empleados_data.json', backup_file)
        print(f"✅ Backup creado: {backup_file}")
        return backup_file
    else:
        print("❌ No se encontró el archivo de datos")
        return None

def enviar_backup_por_email(archivo_backup):
    """Envía el backup por email"""
    
    # Configuración (debes llenar estos datos)
    email_origen = "lemolina0323@gmail.com"  # Tu email
    email_destino = "lemolina0323@gmail.com"  # Email donde recibirás el backup
    password = os.environ.get('EMAIL_PASSWORD', '')  # Contraseña de aplicación de Gmail
    
    if not password:
        print("⚠️ No hay contraseña configurada. Configura EMAIL_PASSWORD en variables de entorno")
        return False
    
    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = email_origen
    msg['To'] = email_destino
    msg['Subject'] = f'Backup Automático Sistema Empleados - {datetime.datetime.now().strftime("%d/%m/%Y")}'
    
    # Cuerpo del email
    cuerpo = f"""
    Backup automático del Sistema de Empleados
    
    Fecha: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    Archivo adjunto: {archivo_backup}
    
    Este backup se genera automáticamente cada 10 días.
    Guarda este archivo en un lugar seguro.
    
    ---
    Sistema de Gestión de Empleados
    """
    
    msg.attach(MIMEText(cuerpo, 'plain'))
    
    # Adjuntar archivo
    try:
        with open(archivo_backup, 'rb') as adjunto:
            parte = MIMEBase('application', 'octet-stream')
            parte.set_payload(adjunto.read())
            encoders.encode_base64(parte)
            parte.add_header('Content-Disposition', f'attachment; filename={os.path.basename(archivo_backup)}')
            msg.attach(parte)
    except Exception as e:
        print(f"❌ Error al adjuntar archivo: {e}")
        return False
    
    # Enviar email
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(email_origen, password)
        servidor.send_message(msg)
        servidor.quit()
        print(f"✅ Backup enviado a {email_destino}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        return False

def backup_automatico():
    """Función principal de backup"""
    print("🔄 Iniciando backup automático...")
    
    # Crear backup
    archivo = crear_backup()
    
    if archivo:
        # Enviar por email
        enviar_backup_por_email(archivo)
        
        # Limpiar backups antiguos (mantener solo los últimos 5)
        limpiar_backups_antiguos()
    
    print("✅ Proceso de backup completado")

def limpiar_backups_antiguos(mantener=5):
    """Elimina backups antiguos, manteniendo solo los últimos N"""
    if os.path.exists('backups'):
        archivos = sorted([f for f in os.listdir('backups') if f.endswith('.json')])
        
        if len(archivos) > mantener:
            for archivo in archivos[:-mantener]:
                os.remove(os.path.join('backups', archivo))
                print(f"🗑️ Backup antiguo eliminado: {archivo}")

if __name__ == '__main__':
    backup_automatico()

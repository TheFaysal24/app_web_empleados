x#!/usr/bin/env python3
"""
Script completo de instalación y configuración
"""
import subprocess
import sys
import os

print("=" * 60)
print("  INSTALACIÓN Y CONFIGURACIÓN AUTOMÁTICA")
print("=" * 60)
print()

# 1. Instalar dependencias
print("📦 Instalando dependencias...")
dependencias = [
    "Flask==2.3.3",
    "Flask-Login==0.6.3",
    "Flask-Limiter==3.5.0",
    "Flask-WTF==1.2.1", 
    "python-dotenv==1.0.0",
    "psycopg2-binary",
    "Flask-Mail",
    "gunicorn==21.2.0"
]

for dep in dependencias:
    print(f"   Instalando {dep}...")
    subprocess.run([sys.executable, "-m", "pip", "install", dep], capture_output=True)

print("✅ Dependencias instaladas\n")

# 2. Crear .env si no existe
if not os.path.exists('.env'):
    print("🔐 Creando archivo .env...")
    import secrets
    secret_key = secrets.token_hex(32)
    with open('.env', 'w') as f:
        f.write(f'SECRET_KEY={secret_key}\n')
        f.write('EMAIL_PASSWORD=\n')
    print("✅ Archivo .env creado\n")
else:
    print("⏭️  Archivo .env ya existe\n")

print()
print("=" * 60)
print("  ✅ INSTALACIÓN COMPLETADA")
print("=" * 60)
print()
print("Próximos pasos:")
print("  1. (Opcional) Editar .env y agregar EMAIL_PASSWORD")
print("  2. Ejecutar: python app.py")
print("  3. Abrir navegador: http://localhost:5000")
print()

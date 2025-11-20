#!/usr/bin/env python
"""
Script para configurar el archivo .env de manera interactiva.
Ayuda al usuario a introducir credenciales de PostgreSQL.
"""

import os
import sys
from pathlib import Path


def setup_env():
    """Configurar el archivo .env de manera interactiva."""
    env_file = Path('.env')
    
    print("=" * 60)
    print("CONFIGURADOR DE ENTORNO - app_web_empleados")
    print("=" * 60)
    print()
    
    # Verificar si .env existe
    if env_file.exists():
        print("✓ Archivo .env encontrado")
        with open(env_file, 'r') as f:
            content = f.read()
        print(f"\nContenido actual:\n{content}")
        response = input("\n¿Deseas actualizar la configuración? (s/n): ").strip().lower()
        if response != 's':
            print("Operación cancelada.")
            return
    
    print("\n" + "=" * 60)
    print("CREDENCIALES DE PostgreSQL")
    print("=" * 60)
    
    # Obtener valores actuales o valores por defecto
    db_host = input("Host PostgreSQL [localhost]: ").strip() or "localhost"
    db_user = input("Usuario PostgreSQL [postgres]: ").strip() or "postgres"
    db_password = input("Contraseña PostgreSQL (requerida): ").strip()
    db_name = input("Nombre de BD [sistema_empleados]: ").strip() or "sistema_empleados"
    
    if not db_password:
        print("\n⚠️  ERROR: La contraseña de PostgreSQL es requerida")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("VALORES ADICIONALES")
    print("=" * 60)
    
    app_tz = input("Zona horaria [America/Bogota]: ").strip() or "America/Bogota"
    secret_key = input("SECRET_KEY de Flask [cambiar en producción]: ").strip() or "dev-secret-key-change-in-production"
    
    # Crear contenido del .env
    env_content = f"""# CONFIGURACION DE ENTORNO
# Generado por setup_env.py

# Configuracion de PostgreSQL (Desarrollo)
DB_HOST={db_host}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_NAME={db_name}

# Para produccion (Render), usar:
# DATABASE_URL=postgresql://usuario:password@host:5432/base_datos

# Zona horaria
APP_TZ={app_tz}

# Seguridad Flask
SECRET_KEY={secret_key}
"""
    
    # Guardar archivo .env
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("\n" + "=" * 60)
    print("✓ CONFIGURACIÓN GUARDADA")
    print("=" * 60)
    print(f"Archivo .env actualizado con éxito")
    print(f"\nConfiguracion guardada:")
    print(f"  - Host: {db_host}")
    print(f"  - Usuario: {db_user}")
    print(f"  - BD: {db_name}")
    print(f"  - Zona horaria: {app_tz}")
    print("\n⚠️  IMPORTANTE:")
    print("  1. Verifica que PostgreSQL esté corriendo")
    print("  2. Cambia SECRET_KEY en producción")
    print("  3. No compartas .env en GitHub (ya está en .gitignore)")
    print("\nAhora puedes ejecutar: python app.py")


if __name__ == "__main__":
    try:
        setup_env()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

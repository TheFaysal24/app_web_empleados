#!/usr/bin/env python3
"""
Script de migración de contraseñas a hash SHA-256
Convierte todas las contraseñas en texto plano a hash seguro
"""

import json
import os
from werkzeug.security import generate_password_hash

DATA_FILE = 'empleados_data.json'

def migrar_contraseñas():
    """Migra todas las contraseñas a hash"""
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: No se encontró {DATA_FILE}")
        return
    
    # Crear backup
    backup_file = f"{DATA_FILE}.backup"
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Backup creado: {backup_file}")
    
    # Migrar contraseñas
    usuarios_migrados = 0
    usuarios_ya_hash = 0
    
    for usuario, info in data.get('usuarios', {}).items():
        if 'contrasena' in info:
            # Verificar si ya está hasheada
            if info['contrasena'].startswith('pbkdf2:sha256:'):
                usuarios_ya_hash += 1
                print(f"⏭️  {usuario}: Ya tiene hash")
            else:
                # Migrar a hash
                password_plano = info['contrasena']
                info['contrasena'] = generate_password_hash(password_plano)
                usuarios_migrados += 1
                print(f"✅ {usuario}: Contraseña migrada a hash")
    
    # Guardar cambios
    if usuarios_migrados > 0:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n🎉 Migración completada:")
        print(f"   - Usuarios migrados: {usuarios_migrados}")
        print(f"   - Ya tenían hash: {usuarios_ya_hash}")
        print(f"   - Total usuarios: {len(data.get('usuarios', {}))}")
    else:
        print(f"\n✅ Todas las contraseñas ya están hasheadas ({usuarios_ya_hash})")
        os.remove(backup_file)
        print(f"🗑️  Backup eliminado (no era necesario)")

if __name__ == '__main__':
    print("🔐 Iniciando migración de contraseñas a hash SHA-256...\n")
    migrar_contraseñas()
    print("\n✅ Proceso completado")

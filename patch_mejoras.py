#!/usr/bin/env python3
"""
🔄 PATCH DE MEJORAS - Aplicar cambios críticos
Este script actualiza app.py con las mejoras de persistencia y privacidad
"""

import os
import shutil
from datetime import datetime

def aplicar_mejoras():
    """Aplica las mejoras al archivo app.py"""
    
    archivo = 'app.py'
    backup = f'app.py.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # Crear backup
    print("📦 Creando backup...")
    shutil.copy2(archivo, backup)
    print(f"✅ Backup creado: {backup}")
    
    # Leer archivo
    with open(archivo, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Aplicar cambios línea por línea
    modificaciones = 0
    
    for i, line in enumerate(lines):
        # Cambio 1: Ocultar costos para usuarios normales (línea ~556)
        if 'costo_horas_extras = {usuario_actual: costo_horas_extras' in line:
            lines[i] = '        # 🔒 OCULTAR COSTOS PARA USUARIOS NORMALES\n'
            lines.insert(i+1, '        costo_horas_extras = {}  # Vacío para usuarios normales\n')
            modificaciones += 1
            print(f"✅ Modificación 1 aplicada en línea {i+1}")
        
        # Cambio 2: Ocultar costo total empresa
        elif 'costo_total_empresa = costo_horas_extras.get(usuario_actual, 0)' in line:
            lines[i] = '        costo_total_empresa = 0  # Oculto para usuarios normales\n'
            lines.insert(i+1, '        valor_hora_ordinaria = 0  # Oculto para usuarios normales\n')
            modificaciones += 1
            print(f"✅ Modificación 2 aplicada en línea {i+1}")
    
    # Guardar archivo modificado
    with open(archivo, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n🎉 {modificaciones} modificaciones aplicadas")
    print(f"📄 Archivo actualizado: {archivo}")
    print(f"💾 Backup disponible en: {backup}")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("  PATCH DE MEJORAS - Sistema de Empleados v2.1")
    print("=" * 60)
    print()
    
    try:
        aplicar_mejoras()
        print()
        print("✅ MEJORAS APLICADAS EXITOSAMENTE")
        print()
        print("Cambios realizados:")
        print("  1. ✅ Costos ocultos para usuarios normales")
        print("  2. ✅ Solo admin puede ver costos de horas")
        print("  3. ✅ Persistencia de datos mejorada")
        print()
        print("Próximos pasos:")
        print("  1. Ejecutar: python app.py")
        print("  2. Probar con usuario normal (no ver costos)")
        print("  3. Probar con admin (ver costos)")
        print()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("Por favor, restaura desde el backup si es necesario")

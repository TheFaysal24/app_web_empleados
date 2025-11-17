#!/usr/bin/env python3
"""
Script para corregir indentación en app.py
"""
import shutil
from datetime import datetime

# Crear backup
backup = f'app.py.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy2('app.py', backup)
print(f"📦 Backup creado: {backup}")

# Leer archivo
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corregir líneas 556-559 (índice 555-558)
# Deben tener 8 espacios de indentación (igual que la línea 555)
modificaciones = 0

for i in range(len(lines)):
    # Línea 556: comentario
    if i == 555 and '# 🔒 OCULTAR COSTOS' in lines[i]:
        lines[i] = '        # 🔒 OCULTAR COSTOS PARA USUARIOS NORMALES\n'
        modificaciones += 1
        print(f"✅ Corregida línea {i+1}")
    
    # Línea 557: costo_horas_extras
    elif i == 556 and 'costo_horas_extras = {}' in lines[i]:
        lines[i] = '        costo_horas_extras = {}  # Vacío para usuarios normales\n'
        modificaciones += 1
        print(f"✅ Corregida línea {i+1}")
    
    # Línea 558: costo_total_empresa
    elif i == 557 and 'costo_total_empresa = 0' in lines[i]:
        lines[i] = '        costo_total_empresa = 0  # Oculto para usuarios normales\n'
        modificaciones += 1
        print(f"✅ Corregida línea {i+1}")
    
    # Línea 559: valor_hora_ordinaria
    elif i == 558 and 'valor_hora_ordinaria = 0' in lines[i]:
        lines[i] = '        valor_hora_ordinaria = 0  # Oculto para usuarios normales\n'
        modificaciones += 1
        print(f"✅ Corregida línea {i+1}")

# Guardar archivo corregido
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\n🎉 {modificaciones} líneas corregidas")
print(f"📄 Archivo actualizado: app.py")
print(f"💾 Backup: {backup}")
print("\n✅ Indentación corregida - Ahora ejecutar: python app.py")

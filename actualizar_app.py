#!/usr/bin/env python3
"""
Script para actualizar app.py con mejoras de persistencia y privacidad
"""

import re

# Leer el archivo
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazo 1: Ocultar costos para usuarios normales
old_text_1 = """        contador_inicios = {usuario_actual: contador_inicios.get(usuario_actual, 0)}
        costo_horas_extras = {usuario_actual: costo_horas_extras.get(usuario_actual, 0)}
        costo_total_empresa = costo_horas_extras.get(usuario_actual, 0)
        total_usuarios_nuevos = 1  # Solo mostrar 1 para el usuario actual"""

new_text_1 = """        contador_inicios = {usuario_actual: contador_inicios.get(usuario_actual, 0)}
        # 🔒 OCULTAR COSTOS PARA USUARIOS NORMALES (Solo admin puede ver)
        costo_horas_extras = {}  # Vacío para usuarios normales
        costo_total_empresa = 0  # Ocultar costo total
        valor_hora_ordinaria = 0  # Ocultar valor hora
        total_usuarios_nuevos = 1  # Solo mostrar 1 para el usuario actual"""

content = content.replace(old_text_1, new_text_1)

# Guardar el archivo
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo app.py actualizado")
print("   - Costos ocultados para usuarios normales")
print("   - Solo admin puede ver costos de horas extras")

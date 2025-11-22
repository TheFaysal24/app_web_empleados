#!/usr/bin/env python3
"""
Script para corregir problemas de indentación en app.py
Convierte tabs a espacios y asegura indentación consistente de 4 espacios.
"""

import re

def fix_indentation(file_path):
    """Corrige la indentación del archivo especificado."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convertir tabs a espacios (4 espacios por tab)
        content = content.expandtabs(4)

        # Asegurar que las líneas no empiecen con espacios inconsistentes
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Si la línea tiene solo espacios, mantenerla como está
            if line.strip() == '':
                fixed_lines.append(line)
                continue

            # Contar espacios iniciales
            leading_spaces = len(line) - len(line.lstrip(' '))

            # Si no es múltiplo de 4, ajustar
            if leading_spaces % 4 != 0:
                # Redondear al múltiplo de 4 más cercano
                corrected_spaces = (leading_spaces // 4) * 4
                line = ' ' * corrected_spaces + line.lstrip(' ')

            fixed_lines.append(line)

        # Unir las líneas
        fixed_content = '\n'.join(fixed_lines)

        # Escribir el archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"✅ Indentación corregida en {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error al corregir indentación: {e}")
        return False

if __name__ == "__main__":
    import sys
    import os

    # Si se pasa un archivo como argumento, usarlo
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        # Por defecto, corregir app.py en el directorio actual
        target_file = 'app.py'

    if os.path.exists(target_file):
        print(f"Corrigiendo indentación en {target_file}...")
        success = fix_indentation(target_file)
        if success:
            print("Indentación corregida exitosamente.")
        else:
            print("Error al corregir la indentación.")
    else:
        print(f"Archivo {target_file} no encontrado.")

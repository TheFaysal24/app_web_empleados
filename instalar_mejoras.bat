@echo off
echo ========================================
echo   INSTALACION DE DEPENDENCIAS
echo ========================================
echo.

echo Instalando dependencias requeridas...
pip install Flask-Limiter==3.5.0
pip install Flask-WTF==1.2.1
pip install python-dotenv==1.0.0

echo.
echo ========================================
echo   APLICANDO MEJORAS
echo ========================================
echo.

python patch_mejoras.py

echo.
echo ========================================
echo   CREANDO ARCHIVO .env
echo ========================================
echo.

python -c "import os; open('.env', 'w').write('SECRET_KEY=' + os.urandom(24).hex() + '\nEMAIL_PASSWORD=')"

echo.
echo ========================================
echo   LISTO!
echo ========================================
echo.
echo Todo configurado correctamente.
echo.
echo Proximos pasos:
echo   1. Editar .env y agregar EMAIL_PASSWORD
echo   2. Ejecutar: python app.py
echo   3. Probar en: http://localhost:5000
echo.
pause

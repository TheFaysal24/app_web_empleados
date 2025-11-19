@echo off
REM Script para validar que todo está listo para GitHub (Windows)

echo ========================================
echo  VERIFICANDO PROYECTO PARA GITHUB
echo ========================================
echo.

REM 1. Verificar .gitignore
echo 1. Verificando .gitignore...
if exist .gitignore (
    findstr /C:".env" .gitignore >nul
    if %ERRORLEVEL% EQU 0 (
        echo    [OK] .env esta en .gitignore
    ) else (
        echo    [ERROR] .env NO esta en .gitignore
        exit /b 1
    )
) else (
    echo    [ERROR] .gitignore no existe
    exit /b 1
)

REM 2. Verificar archivos importantes
echo.
echo 2. Verificando archivos importantes...
set archivos=app.py requirements.txt README.md Procfile CONFIGURACION_HEROKU.txt

for %%f in (%archivos%) do (
    if exist %%f (
        echo    [OK] %%f
    ) else (
        echo    [ERROR] %%f NO EXISTE
    )
)

REM 3. Verificar requirements.txt
echo.
echo 3. Verificando requirements.txt...
findstr /C:"Flask-Limiter" requirements.txt >nul
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Flask-Limiter incluido
) else (
    echo    [ERROR] Flask-Limiter NO incluido
)

findstr /C:"python-dotenv" requirements.txt >nul
if %ERRORLEVEL% EQU 0 (
    echo    [OK] python-dotenv incluido
) else (
    echo    [ERROR] python-dotenv NO incluido
)

findstr /C:"psycopg2-binary" requirements.txt >nul
if %ERRORLEVEL% EQU 0 (
    echo    [OK] psycopg2-binary incluido
) else (
    echo    [ERROR] psycopg2-binary NO incluido
)

REM 4. Estadísticas
echo.
echo 4. Estadisticas del proyecto...
echo    Archivos Python: 
dir /b *.py 2>nul | find /c ".py"
echo    Templates HTML:
dir /b Templates\*.html 2>nul | find /c ".html"

echo.
echo ========================================
echo  VERIFICACION COMPLETADA
echo ========================================
echo.
echo Proximos pasos:
echo   1. git add .
echo   2. git commit -m "Version final para despliegue"
echo   3. git push origin main
echo   4. git push heroku main
echo.
pause

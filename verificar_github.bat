@echo off
setlocal enabledelayedexpansion

REM Script para validar que todo está listo para GitHub (Windows)

REM --- Configuración de Colores (simulado con caracteres) ---
set "COLOR_OK=[OK]"
set "COLOR_ERROR=[ERROR]"
set "COLOR_INFO=[INFO]"

echo ----------------------------------------
echo  VERIFICANDO PROYECTO PARA GITHUB/HEROKU
echo ----------------------------------------
echo.

REM 1. Verificar .gitignore
echo 1. Verificando .gitignore...
if exist .gitignore (
    findstr /C:".env" .gitignore >nul
    if !ERRORLEVEL! EQU 0 (
        echo    %COLOR_OK% .env esta en .gitignore.
    ) else (
        echo    %COLOR_ERROR% .env NO esta en .gitignore. Agregalo para no exponer tus claves.
        goto end_error
    )

    findstr /C:"__pycache__" .gitignore >nul
    if !ERRORLEVEL! EQU 0 (
        echo    %COLOR_OK% __pycache__ esta en .gitignore.
    ) else (
        echo    %COLOR_ERROR% __pycache__ NO esta en .gitignore. Es recomendable agregarlo.
    )

) else (
    echo    %COLOR_ERROR% El archivo .gitignore no existe. Es crucial para la seguridad.
    goto end_error
)

REM 2. Verificar archivos importantes
echo.
echo 2. Verificando archivos importantes...
set "archivos=app.py requirements.txt Procfile"

for %%f in (%archivos%) do (
    if exist %%f (
        echo    %COLOR_OK% Archivo %%f encontrado.
    ) else (
        echo    %COLOR_ERROR% Archivo %%f NO EXISTE. Es requerido para el despliegue.
    )
)

REM 3. Verificar requirements.txt
echo.
echo 3. Verificando requirements.txt...
set "dependencias=Flask-Limiter python-dotenv psycopg2-binary gunicorn"

for %%d in (%dependencias%) do (
    findstr /C:"%%d" requirements.txt >nul
    if !ERRORLEVEL! EQU 0 (
        echo    %COLOR_OK% %%d incluida.
    ) else (
        if "%%d"=="gunicorn" (
            echo    %COLOR_ERROR% %%d NO incluida. Es necesaria para Heroku.
        ) else (
            echo    %COLOR_ERROR% %%d NO incluida.
        )
    )
)

REM 4. Estadísticas
echo.
echo 4. Estadisticas del proyecto...
for /f %%i in ('dir /b *.py 2^>nul ^| find /c ".py"') do set py_count=%%i
echo    %COLOR_INFO% Archivos Python (.py): !py_count!
for /f %%i in ('dir /b Templates\*.html 2^>nul ^| find /c ".html"') do set html_count=%%i
echo    %COLOR_INFO% Templates HTML (.html): !html_count!

echo.
echo ----------------------------------------
echo  VERIFICACION COMPLETADA CON EXITO
echo ----------------------------------------
echo.
echo PROXIMOS PASOS PARA DESPLEGAR:
echo.
echo   1. Anade los cambios al area de preparacion (staging):
echo      git add .
echo.
echo   2. Crea un commit con un mensaje descriptivo:
echo      git commit -m "Tu mensaje sobre los cambios aqui"
echo.
echo   3. Sube los cambios a tu repositorio principal en GitHub:
echo      git push origin main
echo.
echo   4. Despliega los cambios en Heroku:
echo      git push heroku main
echo.
echo   %COLOR_INFO% Si Heroku falla, revisa los logs con: heroku logs --tail
goto:eof

:end_error
echo.
echo ----------------------------------------
echo  VERIFICACION FALLIDA. CORRIGE LOS ERRORES.
echo ----------------------------------------
pause

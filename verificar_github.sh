#!/bin/bash
# Script para validar que todo está listo para GitHub

echo "🔍 VERIFICANDO PROYECTO ANTES DE SUBIR A GITHUB"
echo "================================================"
echo ""

# 1. Verificar .gitignore
echo "1️⃣ Verificando .gitignore..."
if [ -f ".gitignore" ]; then
    if grep -q ".env" .gitignore; then
        echo "   ✅ .env está en .gitignore"
    else
        echo "   ❌ .env NO está en .gitignore"
        exit 1
    fi
else
    echo "   ❌ .gitignore no existe"
    exit 1
fi

# 2. Verificar que .env no se subirá
echo ""
echo "2️⃣ Verificando que .env no se subirá..."
if git check-ignore -q .env 2>/dev/null; then
    echo "   ✅ .env será ignorado por git"
else
    if [ ! -f ".env" ]; then
        echo "   ⚠️  .env no existe (crear con: python -c \"import os; open('.env', 'w').write('SECRET_KEY=' + os.urandom(24).hex())\")"
    else
        echo "   ⚠️  .env existe pero NO está siendo ignorado"
    fi
fi

# 3. Verificar archivos importantes
echo ""
echo "3️⃣ Verificando archivos importantes..."
archivos_importantes=(
    "app.py"
    "requirements.txt"
    "README.md"
    "Templates/turnos_mensual.html"
    "static/modern-design.css"
    ".env.example"
)

for archivo in "${archivos_importantes[@]}"; do
    if [ -f "$archivo" ]; then
        echo "   ✅ $archivo"
    else
        echo "   ❌ $archivo NO EXISTE"
    fi
done

# 4. Verificar dependencias
echo ""
echo "4️⃣ Verificando requirements.txt..."
if grep -q "Flask-Limiter" requirements.txt; then
    echo "   ✅ Flask-Limiter incluido"
else
    echo "   ❌ Flask-Limiter NO incluido"
fi

if grep -q "python-dotenv" requirements.txt; then
    echo "   ✅ python-dotenv incluido"
else
    echo "   ❌ python-dotenv NO incluido"
fi

# 5. Contar archivos
echo ""
echo "5️⃣ Estadísticas del proyecto..."
total_archivos=$(find . -type f -not -path '*/\.*' -not -path '*/__pycache__/*' | wc -l)
echo "   📁 Total archivos: $total_archivos"

total_python=$(find . -name "*.py" | wc -l)
echo "   🐍 Archivos Python: $total_python"

total_html=$(find . -name "*.html" | wc -l)
echo "   📄 Templates HTML: $total_html"

total_md=$(find . -name "*.md" | wc -l)
echo "   📚 Archivos Markdown: $total_md"

echo ""
echo "================================================"
echo "✅ VERIFICACIÓN COMPLETADA"
echo "================================================"
echo ""
echo "Próximos pasos:"
echo "  1. git add ."
echo "  2. git commit -m \"v2.1.0: Sistema completo con mejoras\""
echo "  3. git push origin main"
echo ""

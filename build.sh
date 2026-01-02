#!/bin/bash
set -e # Detener script si hay errores

echo "Configurando entorno virtual..."

# 1. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando venv..."
    python3 -m venv venv
fi

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Instalar dependencias dentro del entorno virtual
echo "Instalando dependencias en venv..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 4. Construir ejecutable
echo "Construyendo ejecutable..."
# --onefile: Crea un solo archivo ejecutable
# --noconsole: No muestra la consola (para aplicaciones GUI)
# --name: Nombre del ejecutable
# --clean: Limpia caché de pyinstaller
# --paths: Asegura que encuentre los módulos en src
pyinstaller --noconsole --onefile --clean --name "Emi-yt-dlp" --paths=src src/main.py

echo "Construcción completada."
echo "El ejecutable se encuentra en la carpeta 'dist/':"
ls -l dist/Emi-yt-dlp

echo "Nota: Puedes borrar la carpeta 'venv' y 'build' si ya no las necesitas, pero 'venv' es útil para desarrollo."

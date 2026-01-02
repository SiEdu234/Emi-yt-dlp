#!/bin/bash
set -e # Detener script si hay errores

echo "Verificando requisitos del sistema..."

# Verificar si tkinter está instalado en el sistema
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "Error: 'tkinter' no está instalado en tu sistema Python."
    echo "Por favor, instálalo ejecutando:"
    echo "sudo apt-get install python3-tk"
    echo "O el comando equivalente para tu distribución de Linux."
    exit 1
fi

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
# --collect-all customtkinter: Importante para incluir temas y assets de la librería
pyinstaller --noconsole --onefile --clean \
    --name "Emi-yt-dlp" \
    --paths=src \
    --collect-all customtkinter \
    --hidden-import=tkinter \
    --hidden-import=PIL \
    --hidden-import=packaging \
    src/main.py

echo "Construcción completada."
echo "El ejecutable se encuentra en la carpeta 'dist/':"
ls -l dist/Emi-yt-dlp

echo "Nota: Si al ejecutarlo no abre nada, intenta ejecutarlo desde la terminal ./dist/Emi-yt-dlp para ver errores."

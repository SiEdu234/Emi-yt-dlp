#!/bin/bash

APP_NAME="Emi-yt-dlp"
EXEC_PATH="$(pwd)/dist/$APP_NAME"
ICON_PATH="$(pwd)/icon.png" # Asumiremos que pondrás un icono aquí, o usaremos uno genérico
DESKTOP_FILE="$HOME/.local/share/applications/$APP_NAME.desktop"

if [ ! -f "$EXEC_PATH" ]; then
    echo "Error: No se encuentra el ejecutable en $EXEC_PATH"
    echo "Por favor, ejecuta ./build.sh primero."
    exit 1
fi

echo "Creando acceso directo en el menú de aplicaciones..."

# Crear archivo .desktop
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Emi YouTube Downloader
Comment=Cliente de descarga para YouTube
Exec=$EXEC_PATH
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Network;Utility;
EOF

chmod +x "$DESKTOP_FILE"

echo "¡Instalación completada!"
echo "Ahora puedes buscar 'Emi YouTube Downloader' en tu menú de aplicaciones."
echo "O ejecutarlo directamente con: $EXEC_PATH"

#!/bin/bash
set -e

# Verificar si gh está instalado
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) no está instalado."
    exit 1
fi

# Obtener la versión
echo "Etiquetas existentes:"
git tag
echo ""
read -p "Introduce el número de versión para este release (ej. v1.1): " VERSION

if [ -z "$VERSION" ]; then
    echo "Error: La versión no puede estar vacía."
    exit 1
fi

# Título y notas
read -p "Título del release (Enter para usar '$VERSION'): " TITLE
TITLE=${TITLE:-$VERSION}

echo "Preparando release $VERSION..."

# 1. Asegurar que estamos al día
git pull origin main

# 2. Crear el tag
git tag -a "$VERSION" -m "$TITLE"

# 3. Subir el tag para disparar GitHub Actions
echo "Subiendo tag a GitHub..."
git push origin "$VERSION"

echo "¡Tag subido exitosamente!"
echo "GitHub Actions ahora comenzará a construir los ejecutables para Linux y Windows."
echo "Puedes ver el progreso aquí: $(gh repo view --json url -q .url)/actions"
echo "Cuando termine, los archivos aparecerán automáticamente en: $(gh repo view --json url -q .url)/releases/tag/$VERSION"


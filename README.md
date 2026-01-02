# Emi yt-dlp Client

Cliente de escritorio para descargar videos de YouTube utilizando la API de `youtube-downloader`.

## Requisitos del Sistema (para ejecutar desde código fuente)
- Python 3.8+
- Servidor `youtube-downloader` en ejecución (por defecto en http://localhost:5000)
- Librerías de Python: `requests`

## Ejecutable (Sin dependencias)

Para generar una aplicación independiente que no requiera instalar Python ni librerías en la máquina cliente:

1. Ejecuta el script de construcción:
   ```bash
   ./build.sh
   ```

2. El ejecutable se generará en la carpeta `dist/`. Puedes copiar este archivo `dist/Emi-yt-dlp` a cualquier computadora (con el mismo sistema operativo) y ejecutarlo directamente.

## Instalación (Desarrollo)

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Asegurarse de que el servidor `youtube-downloader` esté corriendo.

## Uso (Desarrollo)

Ejecutar la aplicación desde el código fuente:
```bash
python3 src/main.py
```

O usar el script de ejecución:
```bash
./run.sh
```

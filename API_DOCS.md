# Documentación de la API de YouTube Downloader

Esta API permite integrar las funcionalidades de descarga de YouTube, X (Twitter), Instagram y Facebook en aplicaciones externas.

## Base URL
Si estás usando un túnel Playit, tu URL base será algo como:
`https://tu-tunel-playit.gl.at` (sin el puerto 5000, ya que el túnel redirige).

Si es local: `http://localhost:5000`

---

## Endpoints

### 1. Obtener Información del Video
Obtiene metadatos, formatos disponibles y subtítulos.

*   **URL:** `/api/video-info`
*   **Método:** `GET`
*   **Parámetros:**
    *   `url` (string): La URL del video (YouTube, X, Instagram, Facebook).

**Ejemplo de solicitud:**
```http
GET /api/video-info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Respuesta Exitosa (JSON):**
```json
{
    "success": true,
    "platform": "youtube",
    "title": "Rick Astley - Never Gonna Give You Up",
    "duration": "3:33",
    "thumbnail": "https://...",
    "available_resolutions": ["1080p", "720p", "480p", ...],
    "available_subtitles": {"en": "English", "es": "Spanish", ...}
}
```

---

### 2. Iniciar Descarga
Inicia el proceso de descarga en segundo plano.

*   **URL:** `/api/download`
*   **Método:** `POST`
*   **Content-Type:** `application/json`
*   **Cuerpo (JSON):**

| Campo | Tipo | Descripción | Default |
| :--- | :--- | :--- | :--- |
| `url` | string | URL del video | **Requerido** |
| `format` | string | `mp4`, `mp3`, `m4a`, `wav`, `mkv`, `webm` | `mp4` |
| `quality` | string | Resolución deseada (ej: `1080p`, `best`) | `best` |
| `audio_only` | bool | `true` para solo audio | `false` |
| `codec` | string | `auto`, `h264`, `h265`, `vp9`, `av1` | `auto` |
| `subtitle_lang`| string | Código de idioma (ej: `es`) para incrustar | `null` |
| `embed_subs` | bool | `true` para quemar/incrustar subtítulos | `false` |

**Ejemplo de solicitud:**
```json
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "mp4",
    "quality": "1080p",
    "codec": "h264"
}
```

**Respuesta Exitosa:**
```json
{
    "success": true,
    "download_id": "550e8400-e29b-41d4-a716-446655440000",
    "is_playlist": false
}
```

---

### 3. Consultar Estado de Descarga
Debes consultar este endpoint periódicamente (polling) para ver el progreso.

*   **URL:** `/api/download-status/<download_id>`
*   **Método:** `GET`

**Respuesta (Progreso):**
```json
{
    "status": "downloading",
    "progress": 45.5,
    "speed": "2.5 MB/s",
    "eta": "30s",
    "message": "Descargando: 45.5%"
}
```

**Respuesta (Completado):**
```json
{
    "status": "complete",
    "progress": 100,
    "filename": "Rick Astley - Never Gonna Give You Up.mp4",
    "message": "Descarga completada"
}
```

---

### 4. Descargar Archivo Final
Una vez que el estado sea `complete`, usa el `filename` para descargar el archivo.

*   **URL:** `/api/download-file/<filename>`
*   **Método:** `GET`

**Ejemplo:**
`GET /api/download-file/Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up.mp4`

---

### 5. Cancelar Descarga
*   **URL:** `/api/cancel-download/<download_id>`
*   **Método:** `POST`

---

### 6. Listar Archivos Disponibles
Muestra todos los archivos que están en la carpeta de descargas del servidor.

*   **URL:** `/api/list-files`
*   **Método:** `GET`

---

### 7. Descargar Solo Subtítulos
*   **URL:** `/api/download-subtitles`
*   **Método:** `POST`
*   **Cuerpo:** `{ "url": "...", "subtitle_langs": ["es", "en"] }`

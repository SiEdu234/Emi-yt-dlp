import requests
import time
import os
import sys

class YouTubeClient:
    def __init__(self, base_url):
        """
        Inicializa el cliente con la URL base del servidor (tu túnel Playit o localhost).
        Ej: base_url = "https://mi-tunel.playit.gg"
        """
        self.base_url = base_url.rstrip('/')

    def get_video_info(self, url):
        """Obtiene metadatos del video (título, formatos, etc)."""
        try:
            resp = requests.get(f"{self.base_url}/api/video-info", params={"url": url}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error de conexión: {e}")
            return None

    def start_download(self, url, format="mp4", quality="best", audio_only=False):
        """Inicia la descarga en el servidor y devuelve el ID de la tarea."""
        payload = {
            "url": url,
            "format": format,
            "quality": quality,
            "audio_only": audio_only
        }
        try:
            resp = requests.post(f"{self.base_url}/api/download", json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success"):
                return data.get("download_id")
            else:
                print(f"Error del servidor: {data.get('error')}")
                return None
        except requests.RequestException as e:
            print(f"Error iniciando descarga: {e}")
            return None

    def get_status(self, download_id):
        """Consulta el estado actual de la descarga."""
        try:
            resp = requests.get(f"{self.base_url}/api/download-status/{download_id}", timeout=5)
            return resp.json()
        except requests.RequestException:
            return {"status": "unknown"}

    def download_file_to_disk(self, filename, local_folder="."):
        """Descarga el archivo final procesado desde el servidor a tu disco local."""
        download_url = f"{self.base_url}/api/download-file/{filename}"
        local_path = os.path.join(local_folder, filename)
        
        print(f"Descargando {filename} desde el servidor...")
        try:
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Barra de progreso simple para la descarga final
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            sys.stdout.write(f"\rRecibiendo archivo: {percent:.1f}%")
                            sys.stdout.flush()
                        
            print(f"\n¡Archivo guardado en {local_path}!")
            return local_path
        except Exception as e:
            print(f"\nError guardando archivo: {e}")
            return None

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    # CAMBIA ESTO POR TU URL DE PLAYIT
    SERVER_URL = "http://localhost:5000" 
    
    print(f"Conectando a {SERVER_URL}...")
    client = YouTubeClient(SERVER_URL)
    
    video_url = input("URL del video: ")
    if not video_url:
        sys.exit(0)

    # 1. Obtener Info
    print("Consultando información...")
    info = client.get_video_info(video_url)
    if info:
        print(f"Detectado: {info.get('title')}")
        
        # 2. Iniciar
        task_id = client.start_download(video_url, quality="best")
        
        if task_id:
            print(f"Descarga iniciada en servidor remoto (ID: {task_id})")
            
            # 3. Polling (Esperar a que termine)
            while True:
                status = client.get_status(task_id)
                state = status.get("status")
                progress = status.get("progress", 0)
                msg = status.get("message", "")
                
                sys.stdout.write(f"\r[Remoto] {state}: {progress}% - {msg}")
                sys.stdout.flush()
                
                if state == "complete":
                    print("\n¡Procesamiento remoto terminado!")
                    # 4. Traer el archivo al PC local
                    client.download_file_to_disk(status.get("filename"))
                    break
                elif state == "error":
                    print(f"\nError: {status.get('error')}")
                    break
                    
                time.sleep(1)

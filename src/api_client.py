import requests
import time
import os

class APIClient:
    def __init__(self, base_url="http://wise-provinces.gl.at.ply.gg:38158/api"):
        self.base_url = base_url

    def check_connection(self):
        """Verifica si el servidor está activo."""
        try:
            # Intentamos conectar a un endpoint ligero o raíz si existe, 
            # pero como es /api, probaremos con video-info sin params que debería dar 400 pero conectar
            response = requests.get(f"{self.base_url}/video-info", timeout=5)
            return True
        except requests.RequestException:
            return False

    def get_video_info(self, url):
        """Obtiene información del video desde la API."""
        try:
            response = requests.get(f"{self.base_url}/video-info", params={"url": url})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error al conectar con la API: {e}")

    def start_download(self, url, options):
        """Inicia la descarga en el servidor."""
        data = {
            "url": url,
            **options
        }
        try:
            response = requests.post(f"{self.base_url}/download", json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error al iniciar descarga: {e}")

    def get_download_status(self, download_id):
        """Obtiene el estado de la descarga."""
        try:
            response = requests.get(f"{self.base_url}/download-status/{download_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error al obtener estado: {e}")

    def download_file(self, filename, destination_folder, progress_callback=None):
        """Descarga el archivo final desde el servidor a la máquina local."""
        import urllib.parse
        
        # Estrategia de descarga: Intentar endpoint seguro, si falla (404), intentar endpoint clásico
        local_filename = os.path.join(destination_folder, filename)
        
        # 1. Intentar endpoint seguro (Query Params)
        try:
            url = f"{self.base_url}/download-file-safe"
            params = {'filename': filename}
            print(f"DEBUG: Intentando descarga segura: {url} params={params}")
            
            with requests.get(url, params=params, stream=True, timeout=30) as r:
                if r.status_code == 404:
                    raise Exception("Endpoint seguro no encontrado (404)")
                r.raise_for_status()
                self._save_stream(r, local_filename, progress_callback)
                return local_filename
                
        except Exception as e_safe:
            print(f"DEBUG: Falló descarga segura: {e_safe}. Intentando método clásico...")
            
            # 2. Intentar endpoint clásico (Path Param) con codificación robusta
            try:
                safe_filename = urllib.parse.quote(filename)
                url = f"{self.base_url}/download-file/{safe_filename}"
                print(f"DEBUG: Intentando descarga clásica: {url}")
                
                with requests.get(url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    self._save_stream(r, local_filename, progress_callback)
                    return local_filename
            except Exception as e_classic:
                raise Exception(f"Error fatal descargando archivo. Seguro: {e_safe}. Clásico: {e_classic}")

    def _save_stream(self, response, local_filename, progress_callback):
        total_length = response.headers.get('content-length')
        with open(local_filename, 'wb') as f:
            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        dl += len(chunk)
                        f.write(chunk)
                        if progress_callback:
                            percent = int(100 * dl / total_length)
                            progress_callback(percent)

    def download_subtitles(self, url, langs, destination_folder):
        """Descarga subtítulos."""
        data = {
            "url": url,
            "subtitle_langs": langs
        }
        try:
            response = requests.post(f"{self.base_url}/download-subtitles", json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                files = result.get('files', [])
                downloaded_files = []
                for filename in files:
                    self.download_file(filename, destination_folder)
                    downloaded_files.append(filename)
                return downloaded_files
            else:
                raise Exception(result.get('error', 'Error desconocido'))
                
        except requests.RequestException as e:
            raise Exception(f"Error al solicitar subtítulos: {e}")

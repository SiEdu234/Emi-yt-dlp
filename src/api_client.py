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
        try:
            # Usar el nuevo endpoint seguro con query params para evitar problemas de encoding en URL
            url = f"{self.base_url}/download-file-safe"
            params = {'filename': filename}
            
            local_filename = os.path.join(destination_folder, filename)
            
            print(f"DEBUG: Solicitando archivo: {url} con params: {params}")
            
            with requests.get(url, params=params, stream=True, timeout=30) as r:
                if r.status_code != 200:
                    print(f"ERROR: Status {r.status_code} - {r.text}")
                    r.raise_for_status()
                
                total_length = r.headers.get('content-length')
                
                with open(local_filename, 'wb') as f:
                    if total_length is None: # no content length header
                        f.write(r.content)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk: # filter out keep-alive new chunks
                                dl += len(chunk)
                                f.write(chunk)
                                if progress_callback:
                                    percent = int(100 * dl / total_length)
                                    progress_callback(percent)
            return local_filename
        except requests.RequestException as e:
            raise Exception(f"Error al descargar archivo final: {e}")
        except IOError as e:
            raise Exception(f"Error al guardar archivo: {e}")

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

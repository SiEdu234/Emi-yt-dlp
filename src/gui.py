import customtkinter as ctk
import threading
import os
import time
import requests
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from api_client import APIClient

# Configuración global de apariencia
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Emi YouTube Downloader Pro")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Icono
        try:
            # Buscar el icono en el directorio actual o en el directorio del proyecto
            icon_path = "Emilia.ico"
            if not os.path.exists(icon_path):
                # Si estamos en src/, el icono está arriba
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(script_dir)
                possible_path = os.path.join(project_root, "Emilia.ico")
                if os.path.exists(possible_path):
                    icon_path = possible_path

            if os.path.exists(icon_path):
                # En Windows usa iconbitmap, en Linux iconphoto
                if os.name == 'nt':
                    self.iconbitmap(icon_path)
                else:
                    # Para Linux necesitamos cargar la imagen y usar ImageTk
                    # IMPORTANTE: Mantener una referencia a la imagen para evitar el Garbage Collector
                    icon_img = Image.open(icon_path)
                    self.app_icon = ImageTk.PhotoImage(icon_img)
                    self.wm_iconphoto(True, self.app_icon)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
            pass

        # Cliente API
        self.api = APIClient()
        self.video_info = None
        self.downloading = False

        # Layout principal (Grid 2 columnas)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (Izquierda) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Emi Downloader", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sakuga_label = ctk.CTkLabel(self.sidebar_frame, text="Amiguitos de SakugaLatam", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
        self.sakuga_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Nueva Búsqueda", command=self.show_download_frame)
        self.sidebar_button_1.grid(row=2, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # --- FRAME PRINCIPAL (Derecha) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Elementos del Frame Principal
        self.create_download_widgets()
        
        # Verificar conexión al inicio
        self.after(100, self.check_server_status)

    def check_server_status(self):
        if not self.api.check_connection():
            messagebox.showwarning("Servidor Desconectado", 
                                 "No se pudo conectar con el servidor de descargas.\n"
                                 "Verifica que el servidor esté activo o revisa tu conexión.")
            self.lbl_status.configure(text="Servidor desconectado", text_color="red")
        else:
            self.lbl_status.configure(text="Conectado al servidor", text_color="green")

    def create_download_widgets(self):
        # Título
        self.label_title = ctk.CTkLabel(self.main_frame, text="Descargar Video", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="w")

        # Input URL
        self.url_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Pega aquí el enlace de YouTube, Facebook, Instagram, X...", height=40)
        self.url_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.btn_search = ctk.CTkButton(self.main_frame, text="Buscar Información", command=self.start_fetch_thread, height=40)
        self.btn_search.grid(row=1, column=1, padx=10, pady=(0, 10))

        # Info del Video (Frame contenedor)
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.info_frame.grid_columnconfigure(1, weight=1)
        self.info_frame.grid_remove() # Ocultar al inicio
        
        # Thumbnail
        self.thumb_label = ctk.CTkLabel(self.info_frame, text="")
        self.thumb_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        self.lbl_video_title = ctk.CTkLabel(self.info_frame, text="Título del Video", font=ctk.CTkFont(size=16, weight="bold"), anchor="w", wraplength=400)
        self.lbl_video_title.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="ew")

        self.lbl_video_details = ctk.CTkLabel(self.info_frame, text="Duración: --:--", text_color="gray", anchor="w")
        self.lbl_video_details.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="ew")

        # Opciones de Descarga
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Selector de Formato
        ctk.CTkLabel(self.options_frame, text="Formato:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_format = ctk.CTkOptionMenu(self.options_frame, values=["mp4", "mp3", "m4a", "mkv", "webm", "gif"])
        self.combo_format.set("mp4")
        self.combo_format.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Selector de Calidad
        ctk.CTkLabel(self.options_frame, text="Calidad:").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.combo_quality = ctk.CTkOptionMenu(self.options_frame, values=["Mejor disponible"])
        self.combo_quality.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        
        # Selector de Codec
        ctk.CTkLabel(self.options_frame, text="Codec (Avanzado):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.combo_codec = ctk.CTkOptionMenu(self.options_frame, values=["auto", "h264", "h265", "vp9", "av1"])
        self.combo_codec.set("auto")
        self.combo_codec.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Selector de Subtítulos
        ctk.CTkLabel(self.options_frame, text="Subtítulos:").grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.combo_subs = ctk.CTkOptionMenu(self.options_frame, values=["Ninguno"])
        self.combo_subs.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")

        # Botón Descargar
        self.btn_download = ctk.CTkButton(self.main_frame, text="INICIAR DESCARGA", command=self.start_download_thread, height=50, font=ctk.CTkFont(size=15, weight="bold"), fg_color="green", hover_color="darkgreen")
        self.btn_download.grid(row=4, column=0, columnspan=2, padx=10, pady=20, sticky="ew")
        self.btn_download.configure(state="disabled")

        # Barra de Progreso y Estado
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=5, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.progress_bar.set(0)
        
        self.lbl_status = ctk.CTkLabel(self.main_frame, text="Listo para buscar", text_color="gray")
        self.lbl_status.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

    def show_download_frame(self):
        # Limpiar interfaz para nueva descarga
        self.url_entry.configure(state="normal")
        self.url_entry.delete(0, 'end')
        self.btn_download.configure(state="disabled")
        self.btn_search.configure(state="normal")
        self.info_frame.grid_remove()
        self.lbl_status.configure(text="Listo para buscar", text_color="gray")
        self.progress_bar.set(0)
        self.downloading = False

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    # --- LÓGICA ---

    def start_fetch_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            self.lbl_status.configure(text="Por favor ingresa una URL válida", text_color="orange")
            return
        
        self.btn_search.configure(state="disabled")
        self.lbl_status.configure(text="Buscando información...", text_color="white")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        threading.Thread(target=self.fetch_info, args=(url,), daemon=True).start()

    def fetch_info(self, url):
        try:
            info = self.api.get_video_info(url)
            self.after(0, self.on_fetch_success, info)
        except Exception as e:
            self.after(0, self.on_fetch_error, str(e))

    def on_fetch_success(self, info):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        self.btn_search.configure(state="normal")
        
        if info.get('success'):
            self.video_info = info
            self.info_frame.grid() # Mostrar panel de info
            
            title = info.get('title', 'Sin título')
            duration = info.get('duration', '??:??')
            platform = info.get('platform', 'video').capitalize()
            thumb_url = info.get('thumbnail')
            
            self.lbl_video_title.configure(text=title)
            self.lbl_video_details.configure(text=f"{platform} • Duración: {duration}")
            
            # Cargar Thumbnail
            if thumb_url:
                threading.Thread(target=self.load_thumbnail, args=(thumb_url,), daemon=True).start()
            
            # Actualizar resoluciones
            resolutions = info.get('available_resolutions', [])
            if resolutions:
                self.combo_quality.configure(values=resolutions)
                self.combo_quality.set(resolutions[0])
            else:
                self.combo_quality.configure(values=["Mejor disponible"])
                self.combo_quality.set("Mejor disponible")

            # Actualizar subtítulos
            subtitles = info.get('available_subtitles', [])
            # Convertir dict o lista a lista de opciones
            sub_opts = ["Ninguno"]
            if isinstance(subtitles, dict):
                sub_opts.extend(subtitles.keys())
            elif isinstance(subtitles, list):
                sub_opts.extend(subtitles)
            
            self.combo_subs.configure(values=sub_opts)
            self.combo_subs.set("Ninguno")

            self.btn_download.configure(state="normal")
            self.lbl_status.configure(text="Video encontrado. Configura y descarga.", text_color="lightgreen")
        else:
            self.on_fetch_error(info.get('error', 'Error desconocido'))

    def load_thumbnail(self, url):
        try:
            response = requests.get(url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            # Redimensionar manteniendo aspecto
            img.thumbnail((150, 150))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.after(0, lambda: self.thumb_label.configure(image=ctk_img, text=""))
        except Exception:
            pass

    def on_fetch_error(self, error):
        self.progress_bar.stop()
        self.btn_search.configure(state="normal")
        self.lbl_status.configure(text=f"Error: {error}", text_color="red")
        messagebox.showerror("Error", error)

    def start_download_thread(self):
        if self.downloading: return
        
        url = self.url_entry.get().strip()
        fmt = self.combo_format.get()
        quality = self.combo_quality.get()
        sub = self.combo_subs.get()
        codec = self.combo_codec.get()
        
        # Pedir carpeta de destino
        dest_folder = filedialog.askdirectory()
        if not dest_folder:
            return

        audio_only = fmt in ['mp3', 'm4a']
        
        options = {
            "format": fmt,
            "resolution": quality,
            "audio_only": audio_only,
            "codec": codec,
            "subtitle_lang": sub if sub != "Ninguno" else None,
            "embed_subs": True if sub != "Ninguno" else False
        }
        
        self.downloading = True
        self.btn_download.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.lbl_status.configure(text="Iniciando descarga remota...", text_color="cyan")
        
        threading.Thread(target=self.process_download, args=(url, options, dest_folder), daemon=True).start()

    def process_download(self, url, options, dest_folder):
        try:
            # 1. Iniciar
            start_resp = self.api.start_download(url, options)
            if not start_resp.get('success'):
                raise Exception(start_resp.get('error'))
            
            download_id = start_resp.get('download_id')
            
            # 2. Polling
            while True:
                status = self.api.get_download_status(download_id)
                state = status.get('status')
                msg = status.get('message', '')
                progress = status.get('progress', 0)
                
                self.after(0, self.update_status, f"Servidor: {msg}", progress / 100)
                
                if state == 'completed':
                    filename = status.get('filename')
                    break
                elif state == 'error':
                    raise Exception(status.get('error'))
                
                time.sleep(1)
            
            # 3. Descargar a local
            if not filename:
                raise Exception("El servidor no devolvió un nombre de archivo válido.")
                
            self.after(0, self.update_status, f"Descargando: {filename}", 0)
            print(f"DEBUG: Iniciando descarga de archivo: {filename} a {dest_folder}")
            
            def dl_progress(p):
                self.after(0, self.update_status, f"Transfiriendo: {p}%", p / 100)
                
            # Asegurar que el directorio existe
            os.makedirs(dest_folder, exist_ok=True)
            
            local_file = self.api.download_file(filename, dest_folder, progress_callback=dl_progress)
            
            # Verificar integridad
            if not os.path.exists(local_file):
                raise Exception(f"El archivo no aparece en: {local_file}")
                
            file_size = os.path.getsize(local_file)
            if file_size == 0:
                raise Exception("El archivo se creó pero está vacío (0 bytes).")

            print(f"DEBUG: Archivo guardado correctamente: {local_file} ({file_size} bytes)")
            self.after(0, self.on_download_complete, local_file)
            
        except Exception as e:
            print(f"ERROR en proceso de descarga: {e}")
            self.after(0, self.on_download_error, str(e))

    def update_status(self, msg, progress_float):
        self.lbl_status.configure(text=msg, text_color="white")
        self.progress_bar.set(progress_float)

    def on_download_complete(self, filepath):
        self.downloading = False
        self.btn_download.configure(state="normal")
        self.url_entry.configure(state="normal")
        self.lbl_status.configure(text=f"¡Completado! Guardado en: {os.path.basename(filepath)}", text_color="lightgreen")
        self.progress_bar.set(1)
        messagebox.showinfo("Éxito", f"Archivo descargado correctamente:\n{filepath}")

    def on_download_error(self, error):
        self.downloading = False
        self.btn_download.configure(state="normal")
        self.url_entry.configure(state="normal")
        self.lbl_status.configure(text=f"Error: {error}", text_color="red")
        self.progress_bar.set(0)
        messagebox.showerror("Error de Descarga", error)

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()

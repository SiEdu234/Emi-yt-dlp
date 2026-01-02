import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import time
from api_client import APIClient

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro (Client)")
        self.root.geometry("700x850")
        self.root.resizable(False, False)
        
        self.api = APIClient()
        
        # Variables
        self.url_var = tk.StringVar()
        self.video_format_var = tk.StringVar()
        self.audio_format_var = tk.StringVar()
        self.subtitle_format_var = tk.StringVar()
        self.output_path_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.status_var = tk.StringVar(value="Listo")
        self.progress_var = tk.DoubleVar()
        
        self.fetching = False
        self.downloading = False
        self.video_info = None
        
        self.setup_style()
        self.create_widgets()
        self.center_window()

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('.', background='#f0f0f0', foreground='#333333')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TEntry', fieldbackground='white', font=('Segoe UI', 10))
        self.style.configure('TCombobox', fieldbackground='white', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('Accent.TButton', foreground='white', background='#0078d7', font=('Segoe UI', 10, 'bold'))
        self.style.map('Accent.TButton', background=[('active', '#005fa3'), ('disabled', '#cccccc')])

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(title_frame, text="YouTube Downloader Pro", font=('Segoe UI', 16, 'bold')).pack()
        ttk.Label(title_frame, text="Cliente Remoto - Sin dependencias locales", font=('Segoe UI', 10), foreground="#666666").pack()
        
        # URL
        url_frame = ttk.LabelFrame(main_frame, text=" URL del video ", padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.pack(fill=tk.X, padx=5, pady=5)
        url_entry.focus()
        
        # Botón Buscar
        self.fetch_btn = ttk.Button(main_frame, text="Buscar Información", command=self.start_fetch_thread, style='Accent.TButton')
        self.fetch_btn.pack(fill=tk.X, pady=10)
        
        # Info del video (oculto al inicio)
        self.info_frame = ttk.LabelFrame(main_frame, text=" Información ", padding=10)
        self.info_label = ttk.Label(self.info_frame, text="")
        self.info_label.pack(fill=tk.X)
        
        # Formatos
        formats_frame = ttk.LabelFrame(main_frame, text=" Opciones ", padding=10)
        formats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(formats_frame, text="Calidad de Video:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.video_format_combobox = ttk.Combobox(formats_frame, textvariable=self.video_format_var, state="readonly", width=50)
        self.video_format_combobox.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(formats_frame, text="Formato de Salida:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.ext_combobox = ttk.Combobox(formats_frame, values=["mp4", "mkv", "webm", "mp3", "m4a"], state="readonly", width=50)
        self.ext_combobox.set("mp4")
        self.ext_combobox.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)

        ttk.Label(formats_frame, text="Subtítulos:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.subtitle_combobox = ttk.Combobox(formats_frame, textvariable=self.subtitle_format_var, state="readonly", width=50)
        self.subtitle_combobox.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # Destino
        dest_frame = ttk.LabelFrame(main_frame, text=" Destino ", padding=10)
        dest_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(dest_frame, textvariable=self.output_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dest_frame, text="...", width=5, command=self.select_output_path).pack(side=tk.RIGHT, padx=5)
        
        # Botones Acción
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=15)
        
        self.download_btn = ttk.Button(buttons_frame, text="Descargar", command=self.start_download_thread, style='Accent.TButton', state="disabled")
        self.download_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.download_subs_btn = ttk.Button(buttons_frame, text="Descargar Solo Subtítulos", command=self.start_subs_download_thread, state="disabled")
        self.download_subs_btn.pack(fill=tk.X)
        
        # Estado y Progreso
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
        
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, font=('Segoe UI', 9), foreground="#666666")
        status_bar.pack(fill=tk.X)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def select_output_path(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path_var.set(path)

    def toggle_inputs(self, enable):
        state = "normal" if enable else "disabled"
        self.fetch_btn.config(state=state)
        self.download_btn.config(state=state if self.video_info else "disabled")
        self.download_subs_btn.config(state=state if self.video_info else "disabled")
        self.video_format_combobox.config(state="readonly" if enable else "disabled")
        self.ext_combobox.config(state="readonly" if enable else "disabled")

    def start_fetch_thread(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Ingresa una URL")
            return
        
        self.fetching = True
        self.toggle_inputs(False)
        self.status_var.set("Obteniendo información del video...")
        self.progress_bar.start(10)
        
        threading.Thread(target=self.fetch_info, args=(url,), daemon=True).start()

    def fetch_info(self, url):
        try:
            info = self.api.get_video_info(url)
            self.root.after(0, self.on_fetch_success, info)
        except Exception as e:
            self.root.after(0, self.on_fetch_error, str(e))

    def on_fetch_success(self, info):
        self.fetching = False
        self.progress_bar.stop()
        self.video_info = info
        
        if info.get('success'):
            self.info_frame.pack(fill=tk.X, pady=5, after=self.fetch_btn)
            title = info.get('title', 'Sin título')
            duration = info.get('duration', '??:??')
            self.info_label.config(text=f"{title}\nDuración: {duration}")
            
            # Llenar resoluciones
            resolutions = info.get('available_resolutions', [])
            self.video_format_combobox['values'] = resolutions
            if resolutions:
                self.video_format_combobox.current(0)
            
            # Llenar subtítulos
            subtitles = info.get('available_subtitles', [])
            sub_values = ["Ninguno"] + subtitles
            self.subtitle_combobox['values'] = sub_values
            self.subtitle_combobox.current(0)
            
            self.status_var.set("Información obtenida correctamente")
            self.toggle_inputs(True)
            self.download_btn.config(state="normal")
            self.download_subs_btn.config(state="normal")
        else:
            self.on_fetch_error(info.get('error', 'Error desconocido'))

    def on_fetch_error(self, error):
        self.fetching = False
        self.progress_bar.stop()
        self.toggle_inputs(True)
        self.status_var.set(f"Error: {error}")
        messagebox.showerror("Error", error)

    def start_download_thread(self):
        if self.downloading: return
        
        url = self.url_var.get().strip()
        resolution = self.video_format_var.get()
        ext = self.ext_combobox.get()
        subtitle = self.subtitle_format_var.get()
        
        audio_only = ext in ['mp3', 'm4a']
        
        options = {
            "format": ext,
            "resolution": resolution,
            "audio_only": audio_only,
            "subtitle_lang": subtitle if subtitle != "Ninguno" else None,
            "embed_subs": True if subtitle != "Ninguno" else False
        }
        
        self.downloading = True
        self.toggle_inputs(False)
        self.status_var.set("Iniciando descarga remota...")
        self.progress_var.set(0)
        
        threading.Thread(target=self.process_download, args=(url, options), daemon=True).start()

    def process_download(self, url, options):
        try:
            # 1. Iniciar descarga
            start_resp = self.api.start_download(url, options)
            if not start_resp.get('success'):
                raise Exception(start_resp.get('error'))
            
            download_id = start_resp.get('download_id')
            
            # 2. Polling de estado
            while True:
                status = self.api.get_download_status(download_id)
                state = status.get('status')
                msg = status.get('message', '')
                progress = status.get('progress', 0)
                
                self.root.after(0, self.update_status, msg, progress)
                
                if state == 'completed':
                    filename = status.get('filename')
                    break
                elif state == 'error':
                    raise Exception(status.get('error'))
                
                time.sleep(1)
            
            # 3. Descargar archivo final
            self.root.after(0, self.update_status, "Descargando archivo a tu PC...", 0)
            dest_folder = self.output_path_var.get()
            
            def dl_progress(p):
                self.root.after(0, self.update_status, f"Transfiriendo: {p}%", p)
                
            local_file = self.api.download_file(filename, dest_folder, progress_callback=dl_progress)
            
            self.root.after(0, self.on_download_complete, local_file)
            
        except Exception as e:
            self.root.after(0, self.on_download_error, str(e))

    def update_status(self, msg, progress):
        self.status_var.set(msg)
        self.progress_var.set(progress)

    def on_download_complete(self, filepath):
        self.downloading = False
        self.toggle_inputs(True)
        self.status_var.set(f"Descarga completada: {os.path.basename(filepath)}")
        self.progress_var.set(100)
        messagebox.showinfo("Éxito", f"Archivo guardado en:\n{filepath}")

    def on_download_error(self, error):
        self.downloading = False
        self.toggle_inputs(True)
        self.status_var.set(f"Error: {error}")
        messagebox.showerror("Error de Descarga", error)

    def start_subs_download_thread(self):
        # Implementación similar para solo subtítulos
        pass

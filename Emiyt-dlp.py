import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import os
import threading
import re

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("700x800")
        self.root.resizable(False, False)
        
        # Variables
        self.url_var = tk.StringVar()
        self.video_format_var = tk.StringVar()
        self.audio_format_var = tk.StringVar()
        self.subtitle_format_var = tk.StringVar()
        self.output_path_var = tk.StringVar(value=os.path.expanduser("~/Downloads/Pruebas"))
        self.formats = []
        self.fetching = False
        self.downloading = False
        
        # Configuración de estilo
        self.setup_style()
        
        # Widgets
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()

    def setup_style(self):
        """Configura los estilos visuales de la aplicación"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuraciones generales
        self.style.configure('.', background='#f0f0f0', foreground='#333333')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TEntry', fieldbackground='white', font=('Segoe UI', 10))
        self.style.configure('TCombobox', fieldbackground='white', font=('Segoe UI', 10))
        
        # Botones
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('Accent.TButton', foreground='white', background='#0078d7', 
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('Accent.TButton', 
                      background=[('active', '#005fa3'), ('disabled', '#cccccc')])

    def create_widgets(self):
        """Crea y organiza los widgets en la ventana"""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(title_frame, 
                 text="YouTube Downloader Pro", 
                 font=('Segoe UI', 16, 'bold'),
                 foreground="#333333").pack()
        
        ttk.Label(title_frame, 
                 text="Descarga videos de YouTube en cualquier formato",
                 font=('Segoe UI', 10),
                 foreground="#666666").pack()
        
        # Entrada de URL
        url_frame = ttk.LabelFrame(main_frame, text=" URL del video ", padding=10)
        url_frame.pack(fill=tk.X, pady=5)
        
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.pack(fill=tk.X, padx=5, pady=5)
        url_entry.focus()
        
        # Botón para buscar formatos
        ttk.Button(main_frame,
                  text="Buscar Formatos Disponibles",
                  command=self.start_fetch_thread,
                  style='Accent.TButton').pack(fill=tk.X, pady=10)
        
        # Frame para formatos
        formats_frame = ttk.LabelFrame(main_frame, text=" Formatos Disponibles ", padding=10)
        formats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Formato de video
        ttk.Label(formats_frame, text="Formato de Video:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.video_format_combobox = ttk.Combobox(formats_frame, 
                                                textvariable=self.video_format_var, 
                                                state="readonly",
                                                width=60)
        self.video_format_combobox.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # Formato de audio
        ttk.Label(formats_frame, text="Formato de Audio (opcional):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.audio_format_combobox = ttk.Combobox(formats_frame, 
                                                 textvariable=self.audio_format_var, 
                                                 state="readonly",
                                                 width=60)
        self.audio_format_combobox.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # Formato de subtítulos
        ttk.Label(formats_frame, text="Subtítulos (opcional):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.subtitle_format_combobox = ttk.Combobox(formats_frame, 
                                                   textvariable=self.subtitle_format_var, 
                                                   state="readonly",
                                                   width=60)
        self.subtitle_format_combobox.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        # Frame para destino
        dest_frame = ttk.LabelFrame(main_frame, text=" Opciones de Descarga ", padding=10)
        dest_frame.pack(fill=tk.X, pady=5)
        
        # Carpeta de destino
        ttk.Label(dest_frame, text="Carpeta de Destino:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(dest_frame, textvariable=self.output_path_var, state="readonly").grid(row=1, column=0, sticky=tk.EW, padx=5)
        ttk.Button(dest_frame, text="Seleccionar", command=self.select_output_path).grid(row=1, column=1, padx=5)
        
        # Botones de descarga
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=15)
        
        self.download_btn = ttk.Button(buttons_frame,
                                      text="Descargar Video",
                                      command=self.start_download_thread,
                                      style='Accent.TButton')
        self.download_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.download_subtitle_btn = ttk.Button(buttons_frame,
                                              text="Descargar Solo Subtítulos",
                                              command=self.start_subtitle_download_thread)
        self.download_subtitle_btn.pack(fill=tk.X)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, 
                               textvariable=self.status_var, 
                               relief=tk.SUNKEN,
                               anchor=tk.W,
                               font=('Segoe UI', 9),
                               foreground="#666666")
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Configurar expansión
        formats_frame.columnconfigure(0, weight=1)
        dest_frame.columnconfigure(0, weight=1)

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def start_fetch_thread(self):
        """Inicia un hilo para buscar formatos sin bloquear la GUI."""
        if self.fetching:
            return
        
        url = self.url_var.get().strip()
        if not self.validate_url(url):
            messagebox.showerror("Error", "Por favor ingresa una URL válida de YouTube.")
            return
        
        self.fetching = True
        self.status_var.set("Buscando formatos disponibles...")
        self.toggle_widgets_state(False)
        
        thread = threading.Thread(target=self.fetch_formats, args=(url,), daemon=True)
        thread.start()

    def validate_url(self, url):
        """Valida que la URL sea de YouTube"""
        patterns = [
            r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(https?://)?(www\.)?youtu\.be/[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+'
        ]
        return any(re.match(pattern, url) for pattern in patterns)

    def fetch_formats(self, url):
        """Obtiene los formatos disponibles (ejecutado en un hilo)."""
        try:
            # Comando para obtener formatos de video y audio
            cmd = [
                "yt-dlp",
                "--no-check-certificate",
                "--skip-download",
                "--print-json",
                "-F",
                url
            ]
            
            # Ejecutar yt-dlp con timeout
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            
            # Procesar la salida para extraer JSON
            json_data = None
            for line in result.stdout.split('\n'):
                try:
                    json_data = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
            
            if not json_data:
                raise ValueError("No se pudo obtener información del video")
            
            # Extraer formatos de la salida completa (no del JSON)
            formats_section = False
            video_formats = []
            audio_formats = []
            
            for line in result.stdout.split('\n'):
                if "ID  EXT   RESOLUTION FPS" in line:
                    formats_section = True
                    continue
                
                if formats_section and line.strip():
                    # Procesamiento de línea mejorado para extraer información simplificada
                    # Ejemplo: 248 - webm - 1080p - 30fps - vp9 - 1.2 GB
                    match = re.search(r'(\d+)\s+(\w+)\s+([^\s]+)\s+([^\s]+)\s+(.*)', line.strip())
                    
                    if match:
                        format_id = match.group(1)
                        ext = match.group(2)
                        resolution = match.group(3)
                        fps = match.group(4)
                        note = match.group(5)
                        
                        # Extraer tamaño de archivo si está disponible
                        size_match = re.search(r'(\d+(\.\d+)?)\s*([KMG]i?B)', note)
                        size_info = f"{size_match.group(0)}" if size_match else "Tamaño desconocido"
                        
                        if "audio only" in note:
                            # Formato simplificado para audio: ID - EXT - CALIDAD - TAMAÑO
                            quality = note.split(',')[0].strip() if ',' in note else note.strip()
                            audio_formats.append(f"{format_id} - {ext.upper()} - {quality} - {size_info}")
                        elif "video only" in note or (ext in ['mp4', 'webm'] and resolution != 'audio'):
                            # Formato simplificado para video: ID - EXT - RESOLUCIÓN - FPS - CODEC - TAMAÑO
                            codec = ""
                            if "vp9" in note: codec = "vp9"
                            elif "avc1" in note: codec = "h264"
                            elif "av1" in note: codec = "av1"
                            
                            video_type = "video+audio" if "video only" not in note else "video only"
                            video_formats.append(f"{format_id} - {ext.upper()} - {resolution} - {fps} - {codec} - {video_type} - {size_info}")
            
            # Obtener información de subtítulos
            subtitle_cmd = [
                "yt-dlp",
                "--no-check-certificate",
                "--skip-download",
                "--list-subs",
                url
            ]
            
            subtitle_result = subprocess.run(subtitle_cmd, capture_output=True, text=True, check=False, timeout=30)
            subtitle_formats = []
            
            # Procesar información de subtítulos
            subtitle_section = False
            for line in subtitle_result.stdout.split('\n'):
                if "Language" in line and "formats" in line:
                    subtitle_section = True
                    continue
                
                if subtitle_section and line.strip() and not line.startswith('WARNING'):
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        lang_code = parts[0]
                        lang_name = parts[1]
                        subtitle_formats.append(f"{lang_code} - {lang_name}")
            
            # Actualizar la GUI
            self.root.after(0, self.update_comboboxes, video_formats, audio_formats, subtitle_formats)
            self.root.after(0, lambda: self.status_var.set(""))
        
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.status_var.set(""))
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                "Tiempo de espera agotado. Verifica tu conexión a internet."))
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() or "No se pudo obtener información del video"
            self.root.after(0, lambda: self.status_var.set(""))
            self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                "Error", 
                f"No se pudieron obtener los formatos:\n{msg}"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(""))
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error inesperado:\n{str(e)}"))
        finally:
            self.root.after(0, self.toggle_widgets_state, True)
            self.fetching = False

    def update_comboboxes(self, video_formats, audio_formats, subtitle_formats=None):
        """Actualiza los comboboxes con los formatos encontrados."""
        self.video_format_combobox['values'] = video_formats
        self.audio_format_combobox['values'] = audio_formats
        
        if subtitle_formats:
            self.subtitle_format_combobox['values'] = subtitle_formats
        
        if video_formats:
            self.video_format_combobox.current(0)
        if audio_formats:
            self.audio_format_combobox.current(0)
        if subtitle_formats:
            self.subtitle_format_combobox.current(0)
        
        if not video_formats and not audio_formats:
            messagebox.showwarning(
                "Advertencia", 
                "No se encontraron formatos disponibles. El video podría estar restringido.")

    def toggle_widgets_state(self, enabled):
        """Habilita o deshabilita los widgets interactivos."""
        state = "normal" if enabled else "disabled"
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Button, ttk.Combobox, ttk.Entry)):
                        try:
                            child["state"] = state
                        except:
                            pass
            elif isinstance(widget, (ttk.Button, ttk.Combobox, ttk.Entry)):
                try:
                    widget["state"] = state
                except:
                    pass

    def select_output_path(self):
        """Abre un diálogo para seleccionar la carpeta de destino."""
        folder = filedialog.askdirectory(initialdir=self.output_path_var.get())
        if folder:
            self.output_path_var.set(folder)

    def start_download_thread(self):
        """Inicia el proceso de descarga en un hilo separado."""
        if self.downloading:
            return
            
        url = self.url_var.get().strip()
        video_format = self.video_format_combobox.get().split()[0] if self.video_format_combobox.get() else None
        audio_format = self.audio_format_combobox.get().split()[0] if self.audio_format_combobox.get() else None
        subtitle_format = self.subtitle_format_combobox.get().split()[0] if self.subtitle_format_combobox.get() else None
        
        if not url or not video_format:
            messagebox.showerror("Error", "Selecciona un formato de video válido.")
            return
        
        # Confirmar descarga
        confirm = messagebox.askyesno(
            "Confirmar descarga",
            "¿Estás seguro de que quieres descargar este video con los formatos seleccionados?")
        
        if confirm:
            self.downloading = True
            self.status_var.set("Preparando descarga...")
            self.toggle_widgets_state(False)
            
            thread = threading.Thread(target=self.run_download, 
                                    args=(url, video_format, audio_format, subtitle_format), 
                                    daemon=True)
            thread.start()

    def start_subtitle_download_thread(self):
        """Inicia el proceso de descarga de subtítulos."""
        if self.downloading:
            return
            
        url = self.url_var.get().strip()
        subtitle_format = self.subtitle_format_combobox.get().split()[0] if self.subtitle_format_combobox.get() else None
        
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL válida.")
            return
        
        if not subtitle_format:
            messagebox.showerror("Error", "Selecciona un formato de subtítulos.")
            return
        
        # Confirmar descarga
        confirm = messagebox.askyesno(
            "Confirmar descarga",
            f"¿Estás seguro de que quieres descargar solo los subtítulos en {subtitle_format}?")
        
        if confirm:
            self.downloading = True
            self.status_var.set("Descargando subtítulos...")
            self.toggle_widgets_state(False)
            
            thread = threading.Thread(target=self.run_subtitle_download, 
                                     args=(url, subtitle_format), 
                                     daemon=True)
            thread.start()

    def run_download(self, url, video_format, audio_format=None, subtitle_format=None):
        """Ejecuta el comando de descarga con optimización de audio profesional."""
        try:
            output_path = self.output_path_var.get()
            output_template = os.path.join(output_path, "%(title)s.%(ext)s")
            
            format_selection = f"{video_format}+{audio_format}" if audio_format else video_format
            
            # Comando base optimizado para la mejor calidad
            cmd = [
                "yt-dlp",
                "-f", format_selection,
                "--merge-output-format", "mp4",
                "--embed-thumbnail",
                "--embed-metadata",
                "--no-post-overwrites",
                "--newline",
                "-o", output_template
            ]
            
            # Agregar opción de subtítulos si están seleccionados
            if subtitle_format:
                cmd.extend(["--write-sub", "--sub-lang", subtitle_format])
            
            # Agregar URL al final
            cmd.append(url)
            
            # Configuración avanzada de entorno
            env = os.environ.copy()
            env["FFMPEG_BINARY"] = "ffmpeg"  # Asegura que use FFmpeg
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Mostrar progreso en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, lambda msg=output.strip(): self.status_var.set(msg))
            
            # Verificar resultado
            return_code = process.poll()
            if return_code == 0:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Éxito", 
                    "Descarga completada correctamente."))
            else:
                error_msg = process.stderr.read()
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    f"Error en la descarga:\n{error_msg or 'Código de error: ' + str(return_code)}"))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error durante la descarga:\n{str(e)}"))
        finally:
            self.root.after(0, lambda: self.status_var.set(""))
            self.root.after(0, self.toggle_widgets_state, True)
            self.downloading = False

    def run_subtitle_download(self, url, subtitle_format):
        """Ejecuta el comando de descarga solo de subtítulos."""
        try:
            output_path = self.output_path_var.get()
            output_template = os.path.join(output_path, "%(title)s.%(ext)s")
            
            # Comando para descargar solo subtítulos
            cmd = [
                "yt-dlp",
                "--skip-download",
                "--write-sub",
                "--sub-lang", subtitle_format,
                "--convert-subs", "srt",  # Convertir a formato SRT
                "-o", output_template,
                url
            ]
            
            # Ejecutar el comando
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Mostrar progreso en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, lambda msg=output.strip(): self.status_var.set(msg))
            
            # Verificar resultado
            return_code = process.poll()
            if return_code == 0:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Éxito", 
                    f"Subtítulos en {subtitle_format} descargados correctamente."))
            else:
                error_msg = process.stderr.read()
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    f"Error en la descarga de subtítulos:\n{error_msg or 'Código de error: ' + str(return_code)}"))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error durante la descarga de subtítulos:\n{str(e)}"))
        finally:
            self.root.after(0, lambda: self.status_var.set(""))
            self.root.after(0, self.toggle_widgets_state, True)
            self.downloading = False

if __name__ == "__main__":
    # Verificar dependencias
    try:
        # Verificar yt-dlp
        yt_dlp_version = subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"yt-dlp versión: {yt_dlp_version}")
        
        # Verificar FFmpeg
        ffmpeg_version = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.split('\n')[0]
        print(f"FFmpeg versión: {ffmpeg_version}")
        
    except FileNotFoundError as e:
        messagebox.showerror(
            "Error crítico",
            f"Falta dependencia requerida:\n\n{str(e)}\n\n"
            "Instala yt-dlp con: pip install yt-dlp\n"
            "Y descarga FFmpeg de: https://ffmpeg.org/")
        exit(1)
    
    # Crear y ejecutar la aplicación
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
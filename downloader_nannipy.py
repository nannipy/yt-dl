# downloader_classic_bootstrap.py

import tkinter as tk
from tkinter import messagebox, filedialog, PhotoImage
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import yt_dlp
import os
import sys
import platform
import threading
import queue

def get_resource_path(relative_path):
    """ Ottiene il percorso assoluto della risorsa, funziona sia in dev che con PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_ffmpeg_path():
    """Trova ffmpeg e ffprobe dentro il bundle dell'app o in locale per lo sviluppo."""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        ffmpeg_path = os.path.join(application_path, "ffmpeg")
        if os.path.exists(ffmpeg_path):
            return application_path
        else:
            if hasattr(sys, '_MEIPASS'): return sys._MEIPASS
    if platform.system() == "Darwin":
        homebrew_path_m1 = "/opt/homebrew/bin"
        if os.path.exists(homebrew_path_m1): return homebrew_path_m1
        homebrew_path_intel = "/usr/local/bin"
        if os.path.exists(homebrew_path_intel): return homebrew_path_intel
    return None

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YT-Downloader")
        self.root.geometry("550x420")
        self.root.resizable(False, False)

        try:
            icon_path = get_resource_path("icon.png")
            self.app_icon = PhotoImage(file=icon_path)
            self.root.iconphoto(False, self.app_icon)
        except Exception as e:
            print(f"Avviso: icon.png non trovata. {e}")

        self.download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.queue = queue.Queue()
        self.cancel_requested = False
        self.is_downloading = False

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=BOTH, expand=YES)

        # Sezione Logo e Titolo
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20), anchor='w')
        
        try:
            logo_path = get_resource_path("logo.png")
            self.logo_image = PhotoImage(file=logo_path)
            logo_label = ttk.Label(header_frame, image=self.logo_image)
            logo_label.pack(side=LEFT, padx=(0, 15))
        except Exception as e:
            print(f"Avviso: logo.png non trovato. {e}")
            ttk.Label(header_frame, text="YT-DL", font=("", 18, "bold")).pack(side=LEFT)

        ttk.Label(header_frame, text="YouTube Downloader by Nannipy", font=("", 16, "bold")).pack(side=LEFT, anchor='w')

        # Sezione Input
        ttk.Label(main_frame, text="Incolla il link di un video o una playlist").pack(fill=X, anchor='w')
        self.url_entry = ttk.Entry(main_frame, font=("", 11))
        self.url_entry.pack(fill=X, pady=(5, 15), ipady=5)

        # Sezione Path
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=X, pady=(0, 20))
        ttk.Label(path_frame, text="Salva in:").pack(side=LEFT, padx=(0, 5))
        self.path_label = ttk.Label(path_frame, text=self.truncate_path(self.download_path))
        self.path_label.pack(side=LEFT, fill=X, expand=YES)
        self.browse_button = ttk.Button(path_frame, text="Sfoglia...", command=self.browse_folder, bootstyle="outline")
        self.browse_button.pack(side=RIGHT)

        # Pulsanti Azione (MP4 e MP3)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=5, ipady=5)

        # Definisci gli stili PRIMA di creare i bottoni
        style = ttk.Style()

        # Colori unici per ciascun bottone
        mp4_color = "#004AAD"
        mp3_color = "#299FD6"

        # Arrotondamento e colore unico
        style.configure("Mp4.TButton",
                background=mp4_color,
                foreground="#fff",
                borderwidth=1,
                focusthickness=3,
                focuscolor=mp4_color,
                relief="flat",
                bordercolor=mp4_color,
                font=("", 11, "bold"),
                anchor="center",
                padding=8,
                roundness=20)
        style.configure("Mp3.TButton",
                background=mp3_color,
                foreground="#fff",
                borderwidth=1,
                focusthickness=3,
                focuscolor=mp3_color,
                relief="flat",
                bordercolor=mp3_color,
                font=("", 11, "bold"),
                anchor="center",
                padding=8,
                roundness=20)

        # Quando cliccato, il colore di ciascun bottone diventa quello dell'altro
        style.map("Mp4.TButton",
              background=[("active", mp3_color), ("disabled", "#7fa7d9")],
              foreground=[("disabled", "#e0e0e0")])
        style.map("Mp3.TButton",
              background=[("active", mp4_color), ("disabled", "#7fbfdf")],
              foreground=[("disabled", "#e0e0e0")])

        self.mp4_button = ttk.Button(
            button_frame,
            text="Scarica MP4",
            command=lambda: self.start_download('mp4'),
            bootstyle="primary",
            style="Mp4.TButton"
        )
        self.mp4_button.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))

        self.mp3_button = ttk.Button(
            button_frame,
            text="Scarica MP3",
            command=lambda: self.start_download('mp3'),
            bootstyle="secondary",
            style="Mp3.TButton"
        )
        self.mp3_button.pack(side=LEFT, fill=X, expand=YES, padx=(5, 0))

        # Sezione Stato e Progresso
        status_container = ttk.Frame(main_frame)
        status_container.pack(fill=X, pady=(15, 0))
        
        self.status_indicator = ttk.Label(status_container, text="●", font=("", 20), bootstyle="secondary")
        self.status_indicator.pack(side=LEFT, padx=(0, 10))

        self.status_label = ttk.Label(status_container, text="Pronto.")
        self.status_label.pack(side=LEFT, anchor='w', fill=X, expand=YES)
        self.cancel_button = ttk.Button(status_container, text="Annulla", command=self.cancel_download, bootstyle="danger", state=DISABLED)
        self.cancel_button.pack(side=RIGHT)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', bootstyle="striped")
        self.progress_bar.pack(fill=X, pady=10)

        self.root.after(100, self.process_queue)
        self.animate_status()

    def animate_status(self):
        if self.is_downloading:
            current_style = self.status_indicator.cget("bootstyle")
            next_style = "info" if current_style == "secondary" else "secondary"
            self.status_indicator.config(bootstyle=next_style)
        else:
            self.status_indicator.config(bootstyle="secondary")
        self.root.after(700, self.animate_status)

    def start_download(self, format_choice):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Errore", "Per favore, inserisci un URL.")
            return
        self.cancel_requested = False
        self.is_downloading = True
        self.status_indicator.config(bootstyle="info")
        self.set_ui_state(DISABLED)
        self.status_label.config(text="Avvio del download...")
        threading.Thread(target=self.run_download, args=(url, format_choice), daemon=True).start()

    def set_ui_state(self, state):
        downloading = (state == DISABLED)
        self.is_downloading = downloading
        for widget in [self.url_entry, self.browse_button, self.mp4_button, self.mp3_button]:
            widget.config(state=state)
        self.cancel_button.config(state=NORMAL if downloading else DISABLED)
        if not downloading:
            self.progress_bar['value'] = 0
            self.status_indicator.config(bootstyle="secondary")

    def cancel_download(self):
        self.status_label.config(text="Annullamento in corso...")
        self.cancel_requested = True

    def run_download(self, url, format_choice):
        try:
            save_path_template = os.path.join(self.download_path, '%(title)s.%(ext)s')
            ffmpeg_location = get_ffmpeg_path()
            ydl_opts = {
                'quiet': True,
                'progress_hooks': [self.progress_hook],
                'outtmpl': save_path_template,
                'ffmpeg_location': ffmpeg_location
            }
            original_audio_selector = 'bestaudio[language!=en]/bestaudio'
            if format_choice == 'mp3':
                self.queue.put(('status', 'Scaricando e convertendo in MP3...'))
                ydl_opts.update({'format': original_audio_selector, 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]})
            else: # mp4
                ydl_opts.update({'format': f'bestvideo[ext=mp4]+({original_audio_selector})/best[ext=mp4]/best'})
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if not self.cancel_requested:
                self.queue.put(('done', "Download completato!"))
        except yt_dlp.utils.DownloadError:
            if self.cancel_requested:
                self.queue.put(('cancelled', "Download annullato."))
            else:
                error_message = ("Errore di download.\n\nPossibili cause:\n- Il video è privato o con restrizioni di età.\n- Il link non è corretto.\n- YouTube potrebbe aver aggiornato il sito.")
                self.queue.put(('error', error_message))
        except Exception as e:
            print(f"ERRORE IMPREVISTO: {e}")
            self.queue.put(('error', f"Errore imprevisto: {str(e)[:100]}..."))

    def progress_hook(self, d):
        if self.cancel_requested: raise yt_dlp.utils.DownloadError("Download annullato dall'utente.")
        if d['status'] == 'downloading':
            percentage_str = d.get('_percent_str', '0.0%').strip().replace('%', '')
            try: percentage = float(percentage_str)
            except (ValueError, TypeError): percentage = 0.0
            status_text = f"Scaricando: {d.get('_percent_str', '')} di {d.get('_total_bytes_str', 'N/A')}"
            self.queue.put(('progress', (percentage, status_text)))
        elif d['status'] == 'finished':
            self.queue.put(('status', 'Download completato, preparazione file...'))

    def process_queue(self):
        try:
            message_type, data = self.queue.get_nowait()
            if message_type == 'progress':
                percentage, status_text = data
                self.progress_bar['value'] = percentage
                self.status_label.config(text=status_text)
            elif message_type == 'status':
                self.status_label.config(text=data)
            elif message_type == 'done':
                self.set_ui_state(NORMAL)
                self.status_label.config(text="Pronto.")
                messagebox.showinfo("Successo", "Download completato con successo!")
            elif message_type == 'cancelled':
                self.set_ui_state(NORMAL)
                self.status_label.config(text="Download annullato.")
            elif message_type == 'error':
                self.set_ui_state(NORMAL)
                self.status_label.config(text="Errore. Riprova.")
                messagebox.showerror("Errore", data)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def browse_folder(self):
        path = filedialog.askdirectory(initialdir=self.download_path, title="Seleziona una cartella")
        if path:
            self.download_path = path
            self.path_label.config(text=self.truncate_path(self.download_path))

    def truncate_path(self, path, max_len=45):
        if len(path) > max_len: return "..." + path[-(max_len-3):]
        return path

if __name__ == '__main__':
    # Usiamo il tema 'cyborg' che corrisponde al look scuro dell'immagine
    root = ttk.Window(themename="cyborg")
    app = YouTubeDownloaderApp(root)
    root.mainloop()
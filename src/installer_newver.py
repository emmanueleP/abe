import os
import sys
import requests
import tempfile
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
from win10toast import ToastNotifier
import psutil
import time

class AutoUpdater(QThread):
    update_progress = pyqtSignal(int)
    update_completed = pyqtSignal(str)
    update_error = pyqtSignal(str)

    def __init__(self, version, release_url):
        super().__init__()
        self.version = version
        self.release_url = release_url
        self.toaster = ToastNotifier()
        
    def download_file(self, url, destination):
        """Scarica il file mostrando il progresso"""
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        downloaded = 0
        
        with open(destination, 'wb') as file:
            for data in response.iter_content(block_size):
                downloaded += len(data)
                file.write(data)
                progress = int((downloaded / total_size) * 100)
                self.update_progress.emit(progress)

    def notify_update(self):
        """Mostra la notifica di Windows con callback"""
        self.toaster.show_toast(
            "Abe-Gestionale",
            f"È disponibile la versione {self.version}. Clicca qui per aggiornare.",
            icon_path="src/assets/logo_abe.ico",
            duration=None,
            threaded=True,
            callback_on_click=self.start_update
        )

    def close_running_instances(self):
        """Chiude tutte le istanze in esecuzione di Abe-Gestionale"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if "Abe-Gestionale" in proc.info['name']:
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass

    def start_update(self):
        """Avvia il processo di aggiornamento"""
        try:
            # Crea una directory temporanea per il download
            temp_dir = tempfile.mkdtemp()
            installer_path = os.path.join(temp_dir, "Abe-Gestionale_Setup.exe")
            
            # Scarica il nuovo installer
            self.download_file(self.release_url, installer_path)
            
            # Chiudi tutte le istanze dell'applicazione
            self.close_running_instances()
            
            # Attendi un momento per assicurarsi che tutto sia chiuso
            time.sleep(2)
            
            # Avvia l'installer
            subprocess.Popen([installer_path, '/SILENT'])
            
            self.update_completed.emit("Aggiornamento completato con successo!")
            
        except Exception as e:
            self.update_error.emit(f"Errore durante l'aggiornamento: {str(e)}")

    def run(self):
        """Esegue il controllo degli aggiornamenti"""
        try:
            # Controlla se c'è un aggiornamento disponibile
            response = requests.get("https://api.github.com/repos/emmanueleP/abe/releases/latest")
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            
            if latest_version > self.version:
                # Trova l'URL dell'installer nella release
                for asset in latest_release["assets"]:
                    if asset["name"].endswith(".exe"):
                        self.release_url = asset["browser_download_url"]
                        break
                
                # Mostra la notifica
                self.notify_update()
            
        except Exception as e:
            self.update_error.emit(f"Errore nel controllo aggiornamenti: {str(e)}")

def check_for_updates(current_version):
    """Funzione di utilità per avviare il controllo degli aggiornamenti"""
    updater = AutoUpdater(current_version, "")
    updater.start()
    return updater 
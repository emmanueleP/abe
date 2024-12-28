import requests
import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QCheckBox, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)  # version, release_notes
    error_occurred = pyqtSignal(str)

    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.api_url = "https://api.github.com/repos/emmanueleP/abe/releases/latest"
        self.is_running = True

    def run(self):
        try:
            if not self.is_running:
                return
                
            response = requests.get(self.api_url)
            response.raise_for_status()
            
            if not self.is_running:
                return
                
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            
            if self._compare_versions(latest_version, self.current_version) > 0:
                self.update_available.emit(
                    latest_version,
                    latest_release['body']
                )
        except Exception as e:
            if self.is_running:
                self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False
        self.wait()  # Aspetta che il thread finisca

    def __del__(self):
        self.stop()

    def _compare_versions(self, version1, version2):
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0

class UpdateDialog(QDialog):
    def __init__(self, parent=None, version=None, release_notes=None):
        super().__init__(parent)
        self.version = version
        self.release_notes = release_notes
        self.setWindowTitle("Aggiornamento Disponibile")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Informazioni aggiornamento
        info_group = QGroupBox("Nuovo Aggiornamento")
        info_layout = QVBoxLayout()
        
        version_label = QLabel(f"Versione {self.version} disponibile!")
        version_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(version_label)
        
        notes_label = QLabel(self.release_notes)
        notes_label.setWordWrap(True)
        info_layout.addWidget(notes_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Barra progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        self.update_button = QPushButton("Aggiorna Ora")
        self.update_button.clicked.connect(self.start_update)
        buttons_layout.addWidget(self.update_button)
        
        remind_button = QPushButton("Ricordamelo Dopo")
        remind_button.clicked.connect(self.accept)
        buttons_layout.addWidget(remind_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def start_update(self):
        # TODO: Implementare il download e l'installazione dell'aggiornamento
        pass

class UpdateSettings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni Aggiornamenti")
        self.setMinimumWidth(400)
        self.load_settings()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Opzioni aggiornamenti
        update_group = QGroupBox("Controllo Aggiornamenti")
        update_layout = QVBoxLayout()
        
        self.auto_check = QCheckBox("Controlla automaticamente gli aggiornamenti")
        self.auto_check.setChecked(self.settings.get("auto_check", True))
        update_layout.addWidget(self.auto_check)
        
        self.auto_install = QCheckBox("Installa automaticamente gli aggiornamenti")
        self.auto_install.setChecked(self.settings.get("auto_install", False))
        update_layout.addWidget(self.auto_install)
        
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        check_now = QPushButton("Controlla Ora")
        check_now.clicked.connect(self.check_updates)
        buttons_layout.addWidget(check_now)
        
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def load_settings(self):
        try:
            config_path = os.path.join('data', 'config', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.settings = config.get('updates', {
                    'auto_check': True,
                    'auto_install': False
                })
        except Exception:
            self.settings = {
                'auto_check': True,
                'auto_install': False
            }

    def save_settings(self):
        try:
            config_path = os.path.join('data', 'config', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            config['updates'] = {
                'auto_check': self.auto_check.isChecked(),
                'auto_install': self.auto_install.isChecked()
            }
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel salvare le impostazioni: {str(e)}")

    def check_updates(self):
        checker = UpdateChecker("1.0.0")  # Versione corrente
        checker.update_available.connect(self.show_update_dialog)
        checker.error_occurred.connect(self.show_error)
        checker.start()

    def show_update_dialog(self, version, release_notes):
        dialog = UpdateDialog(self, version, release_notes)
        dialog.exec_()

    def show_error(self, error):
        QMessageBox.warning(self, "Errore", f"Errore nel controllo aggiornamenti: {error}") 
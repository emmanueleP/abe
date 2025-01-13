import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QFileDialog
)
from PyQt5.QtCore import Qt

class PDFtoASettings:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(self.base_dir, 'data', 'config')
        self.settings_file = os.path.join(self.config_dir, "pdftoa_config.json")
        
        self.default_settings = {
            "output_directory": os.path.join(os.path.expanduser("~"), "Documents", "Abe", "PDFtoA"),
            "last_directory": ""
        }
        self.current_settings = self.load_settings()
        self.ensure_output_directory()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return {**self.default_settings, **json.load(f)}
            return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=4)
        except Exception as e:
            print(f"Errore nel salvare le impostazioni: {e}")

    def ensure_output_directory(self):
        os.makedirs(self.current_settings["output_directory"], exist_ok=True)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Directory Output
        dir_group = QGroupBox("Directory Output Predefinita")
        dir_layout = QHBoxLayout()
        
        self.dir_label = QLabel(pdftoa_settings.current_settings["output_directory"])
        dir_layout.addWidget(self.dir_label)
        
        change_dir_btn = QPushButton("Cambia")
        change_dir_btn.clicked.connect(self.change_output_dir)
        dir_layout.addWidget(change_dir_btn)
        
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)

        # Pulsante salva
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def change_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Directory Output",
            pdftoa_settings.current_settings["output_directory"]
        )
        if dir_path:
            pdftoa_settings.current_settings["output_directory"] = dir_path
            self.dir_label.setText(dir_path)

    def save_settings(self):
        pdftoa_settings.save_settings()
        self.accept()

pdftoa_settings = PDFtoASettings() 
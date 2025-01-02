from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, 
    QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from datetime import datetime
from .settings import avis_settings
import os

class StartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AViS66 - Avvio")
        self.setMinimumWidth(400)
        self.file_path = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Titolo
        title = QLabel("Seleziona un'opzione")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        open_button = QPushButton("Apri Registro Esistente")
        open_button.clicked.connect(self.open_existing)
        buttons_layout.addWidget(open_button)
        
        new_button = QPushButton("Crea Nuovo Registro")
        new_button.clicked.connect(self.create_new)
        buttons_layout.addWidget(new_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def open_existing(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Apri Registro Soci",
            avis_settings.current_settings.get("last_directory", ""),
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            self.file_path = file_path
            avis_settings.current_settings["last_directory"] = os.path.dirname(file_path)
            avis_settings.save_settings()
            self.accept()
    
    def create_new(self):
        year = avis_settings.current_settings.get("default_year", str(datetime.now().year))
        sede = avis_settings.current_settings.get("codice_sede", "0000")
        default_name = f"RegistroSoci_{sede}_{year}.xlsx"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Crea Nuovo Registro",
            os.path.join(avis_settings.current_settings.get("last_directory", ""), default_name),
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            self.file_path = file_path
            avis_settings.current_settings["last_directory"] = os.path.dirname(file_path)
            avis_settings.save_settings()
            self.accept() 
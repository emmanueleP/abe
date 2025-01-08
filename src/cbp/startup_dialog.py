from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, 
    QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from datetime import datetime
from .settings import cbp_settings
import os

class StartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CBP - Avvio")
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
        
        open_button = QPushButton("Apri File Esistente")
        open_button.clicked.connect(self.open_existing)
        buttons_layout.addWidget(open_button)
        
        new_button = QPushButton("Crea Nuovo File")
        new_button.clicked.connect(self.create_new)
        buttons_layout.addWidget(new_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def open_existing(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Apri File CBP",
            cbp_settings.current_settings.get("last_directory", ""),
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            self.file_path = file_path
            cbp_settings.current_settings["last_directory"] = os.path.dirname(file_path)
            cbp_settings.save_settings()
            self.accept()
    
    def create_new(self):
        year = str(datetime.now().year)
        default_name = f"cassa_banca_prepagata_{year}_master.xlsx"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Crea Nuovo File",
            os.path.join(cbp_settings.current_settings.get("last_directory", ""), default_name),
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            self.file_path = file_path
            cbp_settings.current_settings["last_directory"] = os.path.dirname(file_path)
            cbp_settings.save_settings()
            self.accept() 
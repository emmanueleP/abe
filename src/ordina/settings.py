import json
import os
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QSpinBox, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

class OrdinaSettings:
    def __init__(self):
        # Percorsi base
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.config_dir = os.path.join(self.data_dir, 'config')
        
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.settings_file = os.path.join(self.config_dir, "ordina_config.json")
        user_docs = os.path.join(os.path.expanduser("~"), "Documents")
        
        self.default_settings = {
            "theme": "dark",
            "year": str(datetime.now().year),
            "last_protocol_number": 0,
            "protocol_format": "PROT-{year}-{number:05d}",
            "output_directory": os.path.join(user_docs, "Ordina_protocolli"),
            "stamp_image": None,
            "stamp_position": "bottom-right"
        }
        self.current_settings = self.load_settings()
        self.ensure_output_directory()

    def load_settings(self):
        """Carica le impostazioni dal file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return {**self.default_settings, **json.load(f)}
            return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()

    def save_settings(self):
        """Salva le impostazioni su file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=4)
        except Exception as e:
            print(f"Errore nel salvare le impostazioni: {e}")

    def get_theme(self):
        return self.current_settings["theme"]

    def set_theme(self, theme):
        self.current_settings["theme"] = theme
        self.save_settings()

    def get_next_protocol_number(self):
        """Genera il prossimo numero di protocollo"""
        current_year = str(datetime.now().year)
        if current_year != self.current_settings["year"]:
            self.current_settings["year"] = current_year
            self.current_settings["last_protocol_number"] = 0
        
        self.current_settings["last_protocol_number"] += 1
        self.save_settings()
        
        return self.current_settings["protocol_format"].format(
            year=self.current_settings["year"],
            number=self.current_settings["last_protocol_number"]
        )

    def get_output_directory(self):
        """Restituisce il percorso della cartella di output per l'anno corrente"""
        year_folder = os.path.join(
            self.current_settings["output_directory"],
            self.current_settings["year"]
        )
        # Assicurati che la cartella esista
        os.makedirs(year_folder, exist_ok=True)
        return year_folder

    def set_output_directory(self, path):
        """Imposta la directory di output"""
        self.current_settings["output_directory"] = path
        self.save_settings()
        self.ensure_output_directory()

    def ensure_output_directory(self):
        """Assicura che la cartella di output esista"""
        try:
            year_folder = os.path.join(
                self.current_settings["output_directory"],
                self.current_settings["year"]
            )
            os.makedirs(year_folder, exist_ok=True)
        except Exception as e:
            print(f"Errore nella creazione della cartella di output: {e}")

    def reset_protocol_number(self, year=None):
        """
        Resetta il numero di protocollo per l'anno specificato o corrente.
        
        Args:
            year (str, optional): Anno per cui resettare la numerazione.
                                Se None, usa l'anno corrente nelle impostazioni.
        """
        if year:
            self.current_settings["year"] = str(year)
        self.current_settings["last_protocol_number"] = 0
        self.save_settings()

    # ... resto dei metodi esistenti ...

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Tema
        theme_group = QGroupBox("Tema")
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(ordina_settings.get_theme())
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Anno e Reset
        year_group = QGroupBox("Gestione Anno e Protocollo")
        year_layout = QVBoxLayout()
        
        # Anno selector
        year_row = QHBoxLayout()
        year_label = QLabel("Anno:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(int(ordina_settings.current_settings["year"]))
        year_row.addWidget(year_label)
        year_row.addWidget(self.year_spin)
        year_layout.addLayout(year_row)
        
        # Reset button e info
        reset_row = QHBoxLayout()
        reset_button = QPushButton("Azzera Numerazione")
        reset_button.clicked.connect(self.reset_protocol)
        reset_button.setStyleSheet("background-color: #ff9999;")
        
        # Numero corrente
        current_number = ordina_settings.current_settings["last_protocol_number"]
        self.protocol_info = QLabel(f"Ultimo numero: {current_number:05d}")
        
        reset_row.addWidget(self.protocol_info)
        reset_row.addWidget(reset_button)
        year_layout.addLayout(reset_row)
        
        year_group.setLayout(year_layout)
        layout.addWidget(year_group)

        # Directory Output
        dir_group = QGroupBox("Directory Output")
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(ordina_settings.current_settings["output_directory"])
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

    def reset_protocol(self):
        reply = QMessageBox.question(
            self,
            'Conferma Reset',
            f'Vuoi davvero azzerare la numerazione per l\'anno {self.year_spin.value()}?\n'
            'Questa operazione non può essere annullata.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            ordina_settings.reset_protocol_number(str(self.year_spin.value()))
            self.protocol_info.setText("Ultimo numero: 00000")
            QMessageBox.information(
                self,
                "Completato",
                f"Numerazione azzerata per l'anno {self.year_spin.value()}"
            )

    def change_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Directory Output",
            ordina_settings.current_settings["output_directory"]
        )
        if dir_path:
            ordina_settings.set_output_directory(dir_path)
            self.dir_label.setText(dir_path)

    def save_settings(self):
        ordina_settings.set_theme(self.theme_combo.currentText())
        ordina_settings.current_settings["year"] = str(self.year_spin.value())
        ordina_settings.save_settings()
        ordina_settings.ensure_output_directory()
        self.accept()

# Istanza singleton delle impostazioni
ordina_settings = OrdinaSettings() 
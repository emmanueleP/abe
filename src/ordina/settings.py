import json
import os
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QSpinBox, QComboBox, QFileDialog, QMessageBox,
    QTabWidget, QGridLayout, QTextEdit, QFontComboBox, QColorDialog,
    QWidget
)
from PyQt5.QtGui import (
    QFont, QImage, QPainter, QColor, QPixmap
)
from PyQt5.QtCore import Qt, QRectF

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
            "protocol_format": "Prot. N° {number}/{year}",
            "output_directory": os.path.join(user_docs, "Ordina_protocolli"),
            "stamp_image": None,
            "stamp_position": "bottom-right",
            "stamp_settings": {
                "width": 100,
                "height": 100,
                "text": "Avis Comunale\nProt. N° {number}\ndel {date}",
                "font_size": 10,
                "font_family": "Arial",
                "text_color": "#000000"
            }
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
        """Restituisce la directory di output per i file protocollati."""
        year = datetime.now().year
        default_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "Abe",
            "Ordina",
            str(year)
        )
        return self.current_settings.get("output_directory", default_dir)

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
        
        # Crea il tab widget
        tab_widget = QTabWidget()
        
        # Tab Generale (esistente)
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
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
        general_layout.addWidget(theme_group)

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
        general_layout.addWidget(year_group)

        # Directory Output
        dir_group = QGroupBox("Directory Output")
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(ordina_settings.current_settings["output_directory"])
        dir_layout.addWidget(self.dir_label)
        change_dir_btn = QPushButton("Cambia")
        change_dir_btn.clicked.connect(self.change_output_dir)
        dir_layout.addWidget(change_dir_btn)
        dir_group.setLayout(dir_layout)
        general_layout.addWidget(dir_group)

        general_tab.setLayout(general_layout)
        tab_widget.addTab(general_tab, "Generale")
        
        # Tab Timbro
        stamp_tab = QWidget()
        stamp_layout = QVBoxLayout()
        
        # Dimensioni timbro
        size_group = QGroupBox("Dimensioni Timbro")
        size_layout = QGridLayout()
        
        # Larghezza
        size_layout.addWidget(QLabel("Larghezza (px):"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(50, 500)
        self.width_spin.setValue(ordina_settings.current_settings["stamp_settings"]["width"])
        size_layout.addWidget(self.width_spin, 0, 1)
        
        # Altezza
        size_layout.addWidget(QLabel("Altezza (px):"), 1, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(50, 500)
        self.height_spin.setValue(ordina_settings.current_settings["stamp_settings"]["height"])
        size_layout.addWidget(self.height_spin, 1, 1)
        
        size_group.setLayout(size_layout)
        stamp_layout.addWidget(size_group)
        
        # Testo timbro
        text_group = QGroupBox("Testo Timbro")
        text_layout = QVBoxLayout()
        
        self.stamp_text = QTextEdit()
        self.stamp_text.setPlainText(ordina_settings.current_settings["stamp_settings"]["text"])
        text_layout.addWidget(QLabel("Usa {number} per il numero protocollo e {date} per la data"))
        text_layout.addWidget(self.stamp_text)
        
        # Font
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font:"))
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(ordina_settings.current_settings["stamp_settings"]["font_family"]))
        font_layout.addWidget(self.font_combo)
        
        # Dimensione font
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(ordina_settings.current_settings["stamp_settings"]["font_size"])
        font_layout.addWidget(self.font_size)
        
        text_layout.addLayout(font_layout)
        
        # Colore testo
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Colore testo:"))
        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.current_color = QColor(ordina_settings.current_settings["stamp_settings"]["text_color"])
        self.color_button.setStyleSheet(f"background-color: {self.current_color.name()}")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        text_layout.addLayout(color_layout)
        text_group.setLayout(text_layout)
        stamp_layout.addWidget(text_group)
        
        # Anteprima
        preview_group = QGroupBox("Anteprima")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        stamp_layout.addWidget(preview_group)
        
        stamp_tab.setLayout(stamp_layout)
        tab_widget.addTab(stamp_tab, "Timbro")
        
        layout.addWidget(tab_widget)
        
        # Pulsante salva
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
        
        # Aggiorna anteprima iniziale
        self.update_preview()
        
        # Connetti i segnali per l'aggiornamento dell'anteprima
        self.width_spin.valueChanged.connect(self.update_preview)
        self.height_spin.valueChanged.connect(self.update_preview)
        self.stamp_text.textChanged.connect(self.update_preview)
        self.font_combo.currentFontChanged.connect(self.update_preview)
        self.font_size.valueChanged.connect(self.update_preview)

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

    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
            self.update_preview()

    def update_preview(self):
        """Aggiorna l'anteprima del timbro"""
        # Crea un'immagine vuota per l'anteprima
        preview = QImage(self.width_spin.value(), self.height_spin.value(), 
                        QImage.Format_ARGB32)
        preview.fill(Qt.transparent)
        
        # Prepara il painter
        painter = QPainter(preview)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Imposta il font
        font = self.font_combo.currentFont()
        font.setPointSize(self.font_size.value())
        painter.setFont(font)
        
        # Imposta il colore
        painter.setPen(self.current_color)
        
        # Disegna il testo
        text = self.stamp_text.toPlainText()
        text = text.replace("{number}", "12345")
        text = text.replace("{date}", datetime.now().strftime("%d/%m/%Y"))
        
        rect = QRectF(0, 0, preview.width(), preview.height())
        painter.drawText(rect, Qt.AlignCenter, text)
        
        painter.end()
        
        # Mostra l'anteprima
        pixmap = QPixmap.fromImage(preview)
        self.preview_label.setPixmap(pixmap)

    def save_settings(self):
        # Salva le impostazioni esistenti
        ordina_settings.set_theme(self.theme_combo.currentText())
        ordina_settings.current_settings["year"] = str(self.year_spin.value())
        
        # Salva le impostazioni del timbro
        ordina_settings.current_settings["stamp_settings"].update({
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "text": self.stamp_text.toPlainText(),
            "font_family": self.font_combo.currentFont().family(),
            "font_size": self.font_size.value(),
            "text_color": self.current_color.name()
        })
        
        ordina_settings.save_settings()
        ordina_settings.ensure_output_directory()
        self.accept()

# Istanza singleton delle impostazioni
ordina_settings = OrdinaSettings() 
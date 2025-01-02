import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QLineEdit, QFileDialog, QMessageBox,
    QTabWidget, QListWidget, QListWidgetItem, QWidget
)
from PyQt5.QtCore import Qt

class ManRevSettings:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(self.base_dir, 'data', 'config')
        self.settings_file = os.path.join(self.config_dir, "manrev_config.json")
        
        self.default_settings = {
            "capitoli": [],
            "default_place": "Decimoputzu",
            "default_treasurer": "",
            "default_president": "",
            "default_accountant": "",
            "header_image": "",
            "firme": {
                "tesoriere_firma": "",
                "presidente_firma": "",
                "addetto_firma": ""
            }
        }
        self.current_settings = self.load_settings()

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

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setMinimumWidth(600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Crea il tab widget
        tab_widget = QTabWidget()
        
        # Tab Generali
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        # Valori predefiniti
        defaults_group = QGroupBox("Valori Predefiniti")
        defaults_layout = QVBoxLayout()
        
        # Luogo
        place_row = QHBoxLayout()
        place_row.addWidget(QLabel("Luogo:"))
        self.place_input = QLineEdit()
        self.place_input.setText(manrev_settings.current_settings["default_place"])
        place_row.addWidget(self.place_input)
        defaults_layout.addLayout(place_row)
        
        # Tesoriere
        treasurer_row = QHBoxLayout()
        treasurer_row.addWidget(QLabel("Tesoriere:"))
        self.treasurer_input = QLineEdit()
        self.treasurer_input.setText(manrev_settings.current_settings["default_treasurer"])
        treasurer_row.addWidget(self.treasurer_input)
        defaults_layout.addLayout(treasurer_row)
        
        # Presidente
        president_row = QHBoxLayout()
        president_row.addWidget(QLabel("Presidente:"))
        self.president_input = QLineEdit()
        self.president_input.setText(manrev_settings.current_settings["default_president"])
        president_row.addWidget(self.president_input)
        defaults_layout.addLayout(president_row)
        
        # Addetto Contabile
        accountant_row = QHBoxLayout()
        accountant_row.addWidget(QLabel("Addetto Contabile:"))
        self.accountant_input = QLineEdit()
        self.accountant_input.setText(manrev_settings.current_settings["default_accountant"])
        accountant_row.addWidget(self.accountant_input)
        defaults_layout.addLayout(accountant_row)
        
        defaults_group.setLayout(defaults_layout)
        general_layout.addWidget(defaults_group)
        
        # Firme
        signatures_group = QGroupBox("Firme")
        signatures_layout = QVBoxLayout()
        
        # Firma Tesoriere
        self.treasurer_sign = self.create_signature_row("Firma Tesoriere", "tesoriere_firma")
        signatures_layout.addLayout(self.treasurer_sign)
        
        # Firma Presidente
        self.president_sign = self.create_signature_row("Firma Presidente", "presidente_firma")
        signatures_layout.addLayout(self.president_sign)
        
        # Firma Addetto
        self.accountant_sign = self.create_signature_row("Firma Addetto", "addetto_firma")
        signatures_layout.addLayout(self.accountant_sign)
        
        signatures_group.setLayout(signatures_layout)
        general_layout.addWidget(signatures_group)
        
        general_tab.setLayout(general_layout)
        tab_widget.addTab(general_tab, "Generali")
        
        # Tab Capitoli
        capitoli_tab = QWidget()
        capitoli_layout = QVBoxLayout()
        
        # Lista dei capitoli
        capitoli_group = QGroupBox("Gestione Capitoli")
        capitoli_inner_layout = QVBoxLayout()
        
        # Input per nuovo capitolo
        new_capitolo_layout = QHBoxLayout()
        self.new_capitolo_input = QLineEdit()
        self.new_capitolo_input.setPlaceholderText("Inserisci nuovo capitolo...")
        add_button = QPushButton("Aggiungi")
        add_button.clicked.connect(self.add_capitolo)
        new_capitolo_layout.addWidget(self.new_capitolo_input)
        new_capitolo_layout.addWidget(add_button)
        capitoli_inner_layout.addLayout(new_capitolo_layout)
        
        # Lista dei capitoli esistenti
        self.capitoli_list = QListWidget()
        self.capitoli_list.addItems(manrev_settings.current_settings.get("capitoli", []))
        capitoli_inner_layout.addWidget(self.capitoli_list)
        
        # Pulsante rimuovi
        remove_button = QPushButton("Rimuovi Selezionato")
        remove_button.clicked.connect(self.remove_capitolo)
        capitoli_inner_layout.addWidget(remove_button)
        
        capitoli_group.setLayout(capitoli_inner_layout)
        capitoli_layout.addWidget(capitoli_group)
        
        capitoli_tab.setLayout(capitoli_layout)
        tab_widget.addTab(capitoli_tab, "Capitoli")
        
        layout.addWidget(tab_widget)
        
        # Pulsante salva
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        self.setLayout(layout)

    def create_signature_row(self, label_text, key):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        
        path_input = QLineEdit()
        path_input.setText(manrev_settings.current_settings["firme"][key])
        row.addWidget(path_input)
        
        browse_btn = QPushButton("Sfoglia")
        browse_btn.clicked.connect(lambda: self.browse_signature(path_input))
        row.addWidget(browse_btn)
        
        setattr(self, f"{key}_input", path_input)
        return row

    def browse_signature(self, input_widget):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona Firma",
            "",
            "Immagini (*.png *.jpg *.jpeg)"
        )
        if file_path:
            input_widget.setText(file_path)

    def add_capitolo(self):
        """Aggiunge un nuovo capitolo alla lista"""
        capitolo = self.new_capitolo_input.text().strip()
        if capitolo:
            if capitolo not in [self.capitoli_list.item(i).text() 
                              for i in range(self.capitoli_list.count())]:
                self.capitoli_list.addItem(capitolo)
                self.new_capitolo_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Attenzione",
                    "Questo capitolo esiste già!"
                )

    def remove_capitolo(self):
        """Rimuove il capitolo selezionato"""
        current_item = self.capitoli_list.currentItem()
        if current_item:
            self.capitoli_list.takeItem(self.capitoli_list.row(current_item))

    def save_settings(self):
        try:
            # Salva i capitoli
            capitoli = [self.capitoli_list.item(i).text() 
                       for i in range(self.capitoli_list.count())]
            manrev_settings.current_settings["capitoli"] = capitoli
            
            manrev_settings.current_settings.update({
                "default_place": self.place_input.text(),
                "default_treasurer": self.treasurer_input.text(),
                "default_president": self.president_input.text(),
                "default_accountant": self.accountant_input.text(),
                "firme": {
                    "tesoriere_firma": self.tesoriere_firma_input.text(),
                    "presidente_firma": self.presidente_firma_input.text(),
                    "addetto_firma": self.addetto_firma_input.text()
                }
            })
            
            manrev_settings.save_settings()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel salvare le impostazioni: {str(e)}"
            )

# Istanza singleton delle impostazioni
manrev_settings = ManRevSettings() 
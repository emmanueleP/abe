import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QListWidget, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt

class AgendaSettings:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(self.base_dir, 'data', 'config')
        self.settings_file = os.path.join(self.config_dir, "agenda_config.json")
        
        self.default_settings = {
            "categories": [
                "Direttivo", "Assemblea", "Festa sociale",
                "Pagamento fattura", "Scadenze RUNTS", "Altro"
            ]
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
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Gruppo Categorie
        categories_group = QGroupBox("Categorie Eventi")
        categories_layout = QVBoxLayout()
        
        # Lista categorie
        self.categories_list = QListWidget()
        self.categories_list.addItems(agenda_settings.current_settings["categories"])
        categories_layout.addWidget(self.categories_list)
        
        # Input nuova categoria
        input_layout = QHBoxLayout()
        self.new_category_input = QLineEdit()
        self.new_category_input.setPlaceholderText("Nuova categoria...")
        add_btn = QPushButton("Aggiungi")
        add_btn.clicked.connect(self.add_category)
        input_layout.addWidget(self.new_category_input)
        input_layout.addWidget(add_btn)
        categories_layout.addLayout(input_layout)
        
        # Pulsante rimuovi
        remove_btn = QPushButton("Rimuovi Selezionata")
        remove_btn.clicked.connect(self.remove_category)
        categories_layout.addWidget(remove_btn)
        
        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)
        
        # Pulsante salva
        save_btn = QPushButton("Salva")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)

    def add_category(self):
        category = self.new_category_input.text().strip()
        if category:
            if category not in [self.categories_list.item(i).text() 
                              for i in range(self.categories_list.count())]:
                self.categories_list.addItem(category)
                self.new_category_input.clear()
            else:
                QMessageBox.warning(self, "Attenzione", "Questa categoria esiste già!")

    def remove_category(self):
        current_item = self.categories_list.currentItem()
        if current_item:
            self.categories_list.takeItem(self.categories_list.row(current_item))

    def save_settings(self):
        categories = [self.categories_list.item(i).text() 
                     for i in range(self.categories_list.count())]
        agenda_settings.current_settings["categories"] = categories
        agenda_settings.save_settings()
        self.accept()

# Istanza singleton delle impostazioni
agenda_settings = AgendaSettings() 
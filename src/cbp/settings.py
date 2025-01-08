import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QLineEdit, QFileDialog, QMessageBox,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt

class CbpSettings:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(self.base_dir, 'data', 'config')
        self.settings_file = os.path.join(self.config_dir, "cbp_config.json")
        
        self.default_settings = {
            "last_directory": "",
            "default_formulas": {
                "totale_entrate": "=SUM(B2:B10)",
                "totale_uscite": "=SUM(D2:D10)",
                "saldo": "=B11-D11"
            },
            "columns": {
                "entrate": ["Descrizione", "Importo", "Note"],
                "uscite": ["Descrizione", "Importo", "Note"]
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
        self.setWindowTitle("Impostazioni CBP")
        self.setMinimumWidth(600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Crea il tab widget
        tab_widget = QTabWidget()
        
        # Tab Formule
        formulas_tab = QWidget()
        formulas_layout = QVBoxLayout()
        
        # Formule predefinite
        formulas_group = QGroupBox("Formule Predefinite")
        formulas_inner = QVBoxLayout()
        
        # Totale Entrate
        entrate_layout = QHBoxLayout()
        entrate_layout.addWidget(QLabel("Totale Entrate:"))
        self.entrate_formula = QLineEdit()
        self.entrate_formula.setText(cbp_settings.current_settings["default_formulas"]["totale_entrate"])
        entrate_layout.addWidget(self.entrate_formula)
        formulas_inner.addLayout(entrate_layout)
        
        # Totale Uscite
        uscite_layout = QHBoxLayout()
        uscite_layout.addWidget(QLabel("Totale Uscite:"))
        self.uscite_formula = QLineEdit()
        self.uscite_formula.setText(cbp_settings.current_settings["default_formulas"]["totale_uscite"])
        uscite_layout.addWidget(self.uscite_formula)
        formulas_inner.addLayout(uscite_layout)
        
        # Saldo
        saldo_layout = QHBoxLayout()
        saldo_layout.addWidget(QLabel("Saldo:"))
        self.saldo_formula = QLineEdit()
        self.saldo_formula.setText(cbp_settings.current_settings["default_formulas"]["saldo"])
        saldo_layout.addWidget(self.saldo_formula)
        formulas_inner.addLayout(saldo_layout)
        
        formulas_group.setLayout(formulas_inner)
        formulas_layout.addWidget(formulas_group)
        
        # Informazioni sulle formule
        info_label = QLabel(
            "Formule disponibili:\n"
            "- SUM(range): somma i valori nel range\n"
            "- AVG(range): media dei valori\n"
            "- MIN(range): valore minimo\n"
            "- MAX(range): valore massimo\n"
            "- COUNT(range): conta i valori\n"
            "- ROUND(numero): arrotonda il numero\n\n"
            "Esempio: =SUM(B2:B10) somma i valori dalla cella B2 alla B10"
        )
        info_label.setWordWrap(True)
        formulas_layout.addWidget(info_label)
        
        formulas_tab.setLayout(formulas_layout)
        tab_widget.addTab(formulas_tab, "Formule")
        
        # Tab Directory
        dir_tab = QWidget()
        dir_layout = QVBoxLayout()
        
        dir_group = QGroupBox("Directory Predefinita")
        dir_inner = QHBoxLayout()
        
        self.dir_path = QLineEdit()
        self.dir_path.setText(cbp_settings.current_settings["last_directory"])
        dir_inner.addWidget(self.dir_path)
        
        browse_btn = QPushButton("Sfoglia")
        browse_btn.clicked.connect(self.browse_directory)
        dir_inner.addWidget(browse_btn)
        
        dir_group.setLayout(dir_inner)
        dir_layout.addWidget(dir_group)
        
        dir_tab.setLayout(dir_layout)
        tab_widget.addTab(dir_tab, "Directory")
        
        layout.addWidget(tab_widget)
        
        # Pulsante salva
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        self.setLayout(layout)

    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Directory",
            self.dir_path.text()
        )
        if dir_path:
            self.dir_path.setText(dir_path)

    def save_settings(self):
        try:
            cbp_settings.current_settings.update({
                "last_directory": self.dir_path.text(),
                "default_formulas": {
                    "totale_entrate": self.entrate_formula.text(),
                    "totale_uscite": self.uscite_formula.text(),
                    "saldo": self.saldo_formula.text()
                }
            })
            
            cbp_settings.save_settings()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel salvare le impostazioni: {str(e)}"
            )


# Istanza singleton delle impostazioni
cbp_settings = CbpSettings() 
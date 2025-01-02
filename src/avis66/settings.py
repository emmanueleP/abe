import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QGroupBox,
    QHBoxLayout, QComboBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, QWidget, QVBoxLayout, QTabWidget
)
from PyQt5.QtCore import Qt

class AvisSettings:
    def __init__(self):
        # Percorsi base
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.config_dir = os.path.join(self.data_dir, 'config')
        
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.settings_file = os.path.join(self.config_dir, "avis_config.json")
        
        self.default_settings = {
            "theme": "dark",
            "window_size": (1400, 800),
            "window_position": (100, 100),
            "last_import_directory": "",
            "last_export_directory": "",
            "column_names": {
                "A": "ANNORIFERIMENTO",
                "B": "CODICESEDE",
                "C": "COGNOME",
                "D": "NOME",
                "E": "DATANASCITA",
                "F": "GENERE",
                "G": "CODICEFISCALE",
                "H": "LUOGONASCITA",
                "I": "PROVNASCITA",
                "J": "INDIRIZZO",
                "K": "COMUNE",
                "L": "PROVINCIA",
                "M": "CAP",
                "N": "CELLULARENONDISP",
                "O": "CELLULARE",
                "P": "EMAILNONDISP",
                "Q": "EMAIL",
                "R": "PEC",
                "S": "DATAISCRIZIONE",
                "T": "TESSERA",
                "U": "TIPOSOCIO",
                "V": "DATACESSAZIONE",
                "W": "CAUSACESSAZIONE"
            },
            "codice_sede": "0000",
            "default_year": str(datetime.now().year),
            "last_directory": ""
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
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=4)
        except Exception as e:
            print(f"Errore nel salvare le impostazioni: {e}")

    def get_theme(self):
        return self.current_settings["theme"]

    def set_theme(self, theme):
        self.current_settings["theme"] = theme
        self.save_settings()

    def get_column_name(self, column_letter):
        return self.current_settings["column_names"].get(column_letter, column_letter)

    def set_column_name(self, column_letter, name):
        self.current_settings["column_names"][column_letter] = name
        self.save_settings()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Crea il tab widget
        tab_widget = QTabWidget()
        
        # Tab Generali
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        # Tema
        theme_group = QGroupBox("Tema")
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(avis_settings.get_theme())
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        general_layout.addWidget(theme_group)
        
        # Codice Sede e Anno
        sede_group = QGroupBox("Impostazioni Registro")
        sede_layout = QVBoxLayout()
        
        # Codice Sede
        sede_row = QHBoxLayout()
        sede_row.addWidget(QLabel("Codice Sede:"))
        self.sede_input = QLineEdit()
        self.sede_input.setText(avis_settings.current_settings["codice_sede"])
        sede_row.addWidget(self.sede_input)
        sede_layout.addLayout(sede_row)
        
        # Anno Predefinito
        year_row = QHBoxLayout()
        year_row.addWidget(QLabel("Anno Predefinito:"))
        self.year_input = QLineEdit()
        self.year_input.setText(avis_settings.current_settings["default_year"])
        year_row.addWidget(self.year_input)
        sede_layout.addLayout(year_row)
        
        sede_group.setLayout(sede_layout)
        general_layout.addWidget(sede_group)
        
        # Directory predefinite
        dir_group = QGroupBox("Directory Predefinite")
        dir_layout = QVBoxLayout()
        
        # Import directory
        import_layout = QHBoxLayout()
        import_label = QLabel("Import:")
        self.import_path = QLabel(avis_settings.current_settings["last_import_directory"])
        import_btn = QPushButton("Cambia")
        import_btn.clicked.connect(self.change_import_dir)
        import_layout.addWidget(import_label)
        import_layout.addWidget(self.import_path)
        import_layout.addWidget(import_btn)
        dir_layout.addLayout(import_layout)
        
        # Export directory
        export_layout = QHBoxLayout()
        export_label = QLabel("Export:")
        self.export_path = QLabel(avis_settings.current_settings["last_export_directory"])
        export_btn = QPushButton("Cambia")
        export_btn.clicked.connect(self.change_export_dir)
        export_layout.addWidget(export_label)
        export_layout.addWidget(self.export_path)
        export_layout.addWidget(export_btn)
        dir_layout.addLayout(export_layout)
        
        dir_group.setLayout(dir_layout)
        general_layout.addWidget(dir_group)
        
        general_tab.setLayout(general_layout)
        tab_widget.addTab(general_tab, "Generali")
        
        # Tab Colonne
        columns_tab = QWidget()
        columns_layout = QVBoxLayout()
        
        # Valori Prima Riga
        info_label = QLabel("Modifica i valori predefiniti che appariranno nella prima riga della tabella:")
        info_label.setWordWrap(True)
        columns_layout.addWidget(info_label)
        
        # Tabella per modificare i valori predefiniti
        self.columns_table = QTableWidget()
        self.columns_table.setColumnCount(2)
        self.columns_table.setHorizontalHeaderLabels(["Colonna", "Valore Predefinito"])
        self.columns_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Popola la tabella
        column_names = avis_settings.current_settings["column_names"]
        self.columns_table.setRowCount(len(column_names))
        for i, (col, name) in enumerate(column_names.items()):
            col_item = QTableWidgetItem(f"Colonna {col}")
            col_item.setFlags(col_item.flags() & ~Qt.ItemIsEditable)
            col_item.setBackground(Qt.lightGray)
            name_item = QTableWidgetItem(name)
            self.columns_table.setItem(i, 0, col_item)
            self.columns_table.setItem(i, 1, name_item)
        
        columns_layout.addWidget(self.columns_table)
        
        # Pulsante reset
        reset_btn = QPushButton("Ripristina Valori Originali")
        reset_btn.clicked.connect(self.reset_column_names)
        columns_layout.addWidget(reset_btn)
        
        columns_tab.setLayout(columns_layout)
        tab_widget.addTab(columns_tab, "Colonne")
        
        layout.addWidget(tab_widget)
        
        # Pulsante salva
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        self.setLayout(layout)

    def change_import_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Directory Import",
            avis_settings.current_settings["last_import_directory"]
        )
        if dir_path:
            avis_settings.current_settings["last_import_directory"] = dir_path
            self.import_path.setText(dir_path)

    def change_export_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Directory Export",
            avis_settings.current_settings["last_export_directory"]
        )
        if dir_path:
            avis_settings.current_settings["last_export_directory"] = dir_path
            self.export_path.setText(dir_path)

    def save_settings(self):
        # Salva il tema
        avis_settings.set_theme(self.theme_combo.currentText())
        
        # Salva i nomi delle colonne
        for row in range(self.columns_table.rowCount()):
            col = chr(65 + row)  # A, B, C, ...
            name = self.columns_table.item(row, 1).text()
            avis_settings.set_column_name(col, name)
        
        avis_settings.current_settings.update({
            "codice_sede": self.sede_input.text(),
            "default_year": self.year_input.text()
        })
        
        avis_settings.save_settings()
        self.accept()

    def reset_column_names(self):
        """Ripristina i valori predefiniti originali"""
        reply = QMessageBox.question(
            self,
            'Conferma Ripristino',
            'Vuoi davvero ripristinare i valori originali?\n'
            'Questa operazione non può essere annullata.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for row in range(self.columns_table.rowCount()):
                col = chr(65 + row)  # A, B, C, ...
                name_item = QTableWidgetItem(avis_settings.default_settings["column_names"][col])
                self.columns_table.setItem(row, 1, name_item)


# Istanza singleton delle impostazioni
avis_settings = AvisSettings() 
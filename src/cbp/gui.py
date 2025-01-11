from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QMessageBox, QFileDialog, QMenu, QAction, QInputDialog,
    QHeaderView, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import pandas as pd
import numpy as np
from .calculator import FormulaCalculator
from .settings import cbp_settings
from .startup_dialog import StartupDialog
from .filter_dialog import FilterDialog
from .search_dialog import SearchDialog
import os
from .logic_manager import LogicManager
from ..utils import get_asset_path

class CbpGUI(QMainWindow):
    closed = pyqtSignal()
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.calculator = FormulaCalculator()
        self.logic_manager = LogicManager(self)
        
        # Mostra il dialogo di avvio
        startup = StartupDialog(self)
        if startup.exec_() == QDialog.Accepted and startup.file_path:
            self.file_path = startup.file_path
            
            # Setup dell'interfaccia
            self.setup_menu()
            self.setup_ui()
            
            # Carica o crea il file
            if os.path.exists(self.file_path):
                self.load_data()
            else:
                self.new_file()
            
            # Applica il tema
            if self.app:
                self.apply_theme()
        else:
            # Se l'utente annulla, chiudi l'applicazione
            self.close()
    
    def setup_ui(self):
        self.setWindowTitle("CBP - Cassa Banca Prepagata")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        self.setup_toolbar()  # Aggiungi la toolbar qui, una sola volta
        
        # Tabelle affiancate
        tables_layout = QHBoxLayout()
        
        # Tabella Entrate
        entrate_layout = QVBoxLayout()
        entrate_label = QLabel("ENTRATE")
        entrate_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        entrate_layout.addWidget(entrate_label)
        
        self.entrate_table = QTableWidget()
        self.setup_table(self.entrate_table, "entrate")
        entrate_layout.addWidget(self.entrate_table)
        
        # Totale Entrate
        self.totale_entrate_label = QLabel("Totale: € 0,00")
        entrate_layout.addWidget(self.totale_entrate_label)
        
        tables_layout.addLayout(entrate_layout)
        
        # Tabella Uscite
        uscite_layout = QVBoxLayout()
        uscite_label = QLabel("USCITE")
        uscite_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        uscite_layout.addWidget(uscite_label)
        
        self.uscite_table = QTableWidget()
        self.setup_table(self.uscite_table, "uscite")
        uscite_layout.addWidget(self.uscite_table)
        
        # Totale Uscite
        self.totale_uscite_label = QLabel("Totale: € 0,00")
        uscite_layout.addWidget(self.totale_uscite_label)
        
        tables_layout.addLayout(uscite_layout)
        
        layout.addLayout(tables_layout)
        
        # Saldo finale
        saldo_layout = QHBoxLayout()
        saldo_label = QLabel("SALDO:")
        saldo_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.saldo_value = QLabel("€ 0,00")
        self.saldo_value.setStyleSheet("font-size: 16px;")
        saldo_layout.addWidget(saldo_label)
        saldo_layout.addWidget(self.saldo_value)
        saldo_layout.addStretch()
        
        layout.addLayout(saldo_layout)
        
        # Connessioni
        self.entrate_table.itemChanged.connect(self.calculate_totals)
        self.uscite_table.itemChanged.connect(self.calculate_totals)

    def setup_table(self, table, table_type):
        """Imposta la struttura della tabella"""
        # Imposta le colonne dalla configurazione
        columns = cbp_settings.current_settings["columns"][table_type]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(20)  # Righe iniziali
        
        # Imposta le proprietà della tabella
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Descrizione
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Importo
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Note
        table.setColumnWidth(1, 150)  # Larghezza fissa per importo
        
        # Imposta il menu contestuale
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda pos, t=table: self.show_context_menu(pos, t)
        )
    
    def show_context_menu(self, pos, table):
        menu = QMenu()
        
        insert_row = menu.addAction("Inserisci Riga")
        delete_row = menu.addAction("Elimina Riga")
        menu.addSeparator()
        add_formula = menu.addAction("Aggiungi Formula")
        
        action = menu.exec_(table.mapToGlobal(pos))
        
        if action == insert_row:
            self.insert_row(table)
        elif action == delete_row:
            self.delete_row(table)
        elif action == add_formula:
            self.add_formula(table)
    
    def calculate_totals(self):
        # Calcola totale entrate
        entrate_total = self.calculate_table_total(self.entrate_table)
        self.totale_entrate_label.setText(f"Totale: € {entrate_total:,.2f}")
        
        # Calcola totale uscite
        uscite_total = self.calculate_table_total(self.uscite_table)
        self.totale_uscite_label.setText(f"Totale: € {uscite_total:,.2f}")
        
        # Calcola saldo
        saldo = entrate_total - uscite_total
        color = "green" if saldo >= 0 else "red"
        self.saldo_value.setStyleSheet(f"font-size: 16px; color: {color};")
        self.saldo_value.setText(f"€ {saldo:,.2f}")
    
    def calculate_table_total(self, table):
        total = 0
        for row in range(table.rowCount()):
            item = table.item(row, 1)  # Colonna importo
            if item and item.text():
                try:
                    if item.text().startswith("="):
                        # È una formula
                        value = self.calculator.evaluate(item.text(), table)
                    else:
                        # È un numero
                        value = float(item.text().replace("€", "").replace(",", ""))
                    total += value
                except:
                    pass
        return total 

    def setup_toolbar(self):
        """Imposta la toolbar"""
        toolbar = self.addToolBar("Strumenti")
        
        # Nuovo file
        new_action = QAction(QIcon(get_asset_path('add.png')), "Nuovo", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        # Apri file
        open_action = QAction(QIcon(get_asset_path('open.png')), "Apri", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_data)
        toolbar.addAction(open_action)
        
        # Salva file
        save_action = QAction(QIcon(get_asset_path('diskette.png')), "Salva", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Pulsante Ricerca
        search_action = QAction(QIcon(get_asset_path('search.png')), "Cerca", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self.show_search)
        toolbar.addAction(search_action)
        
        # Pulsante Filtro
        filter_action = QAction(QIcon(get_asset_path('filter.png')), "Filtri", self)
        filter_action.triggered.connect(self.show_filters)
        toolbar.addAction(filter_action)
        
        toolbar.addSeparator()
        
        # Aggiungi riga
        add_row_action = QAction(QIcon(get_asset_path('add.png')), "Aggiungi Riga", self)
        add_row_action.triggered.connect(lambda: self.insert_row(self.get_current_table()))
        toolbar.addAction(add_row_action)
        
        # Rimuovi riga
        remove_row_action = QAction(QIcon(get_asset_path('trash.png')), "Rimuovi Riga", self)
        remove_row_action.triggered.connect(lambda: self.delete_row(self.get_current_table()))
        toolbar.addAction(remove_row_action)

    def setup_menu(self):
        """Imposta il menu"""
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("Nuovo", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Apri...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_data)
        file_menu.addAction(open_action)
        
        save_action = QAction("Salva", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Esci", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Modifica
        edit_menu = menubar.addMenu("Modifica")
        
        add_row_action = QAction("Aggiungi Riga", self)
        add_row_action.triggered.connect(lambda: self.insert_row(self.get_current_table()))
        edit_menu.addAction(add_row_action)
        
        remove_row_action = QAction("Rimuovi Riga", self)
        remove_row_action.triggered.connect(lambda: self.delete_row(self.get_current_table()))
        edit_menu.addAction(remove_row_action)
        
        # Menu Impostazioni
        settings_menu = menubar.addMenu("Impostazioni")
        
        settings_action = QAction("Configura...", self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)

    def get_current_table(self):
        """Restituisce la tabella attualmente selezionata"""
        if self.entrate_table.hasFocus():
            return self.entrate_table
        return self.uscite_table

    def insert_row(self, table):
        """Inserisce una nuova riga nella tabella"""
        current_row = table.currentRow()
        table.insertRow(current_row + 1)

    def delete_row(self, table):
        """Elimina la riga selezionata"""
        current_row = table.currentRow()
        if current_row >= 0:
            table.removeRow(current_row)
            self.calculate_totals()

    def show_settings(self):
        """Mostra la finestra delle impostazioni"""
        from .settings import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec_()

    def new_file(self):
        """Crea un nuovo file"""
        return self.logic_manager.create_new_file()
    
    def load_data(self):
        """Carica i dati da un file esistente"""
        return self.logic_manager.load_file()
    
    def save_file(self):
        """Salva il file corrente"""
        if hasattr(self, 'file_path') and self.file_path:
            if self.logic_manager.save_file():
                self.statusBar().showMessage("File salvato con successo", 3000)

    def apply_theme(self):
        """Applica il tema all'applicazione"""
        if self.app:
            from qt_material import apply_stylesheet
            theme = "dark_teal.xml"
            apply_stylesheet(self.app, theme=theme)

    def closeEvent(self, event):
        """Gestisce la chiusura della finestra"""
        self.closed.emit()
        event.accept() 

    def show_search(self):
        """Mostra la barra di ricerca"""
        search_dialog = SearchDialog(self)
        if search_dialog.exec_() == QDialog.Accepted:
            search_text = search_dialog.search_text.lower()
            self.apply_search(search_text)

    def apply_search(self, search_text):
        """Applica la ricerca alle tabelle"""
        for table in [self.entrate_table, self.uscite_table]:
            for row in range(table.rowCount()):
                row_visible = False
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item and search_text in item.text().lower():
                        row_visible = True
                        break
                table.setRowHidden(row, not row_visible)

    def show_filters(self):
        """Mostra il dialog dei filtri"""
        filter_dialog = FilterDialog(self)
        filter_dialog.exec_()

    def apply_filter(self, table, column, values):
        """Applica il filtro alla tabella"""
        for row in range(table.rowCount()):
            item = table.item(row, column)
            if item:
                table.setRowHidden(row, item.text() not in values) 
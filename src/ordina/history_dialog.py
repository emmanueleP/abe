from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import pandas as pd
import os
from datetime import datetime
from .settings import ordina_settings

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cronologia Protocolli")
        self.setGeometry(100, 100, 800, 600)
        self.history_file = self.get_history_file()
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Barra di ricerca
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca protocollo...")
        self.search_input.textChanged.connect(self.search_protocol)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tabella
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Protocollo", "Data", "Ora", "File"])
        
        # Configura la tabella
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.doubleClicked.connect(self.open_file)
        
        layout.addWidget(self.table)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        open_file_btn = QPushButton("Apri File")
        open_file_btn.clicked.connect(self.open_file)
        buttons_layout.addWidget(open_file_btn)
        
        open_folder_btn = QPushButton("Apri Cartella")
        open_folder_btn.clicked.connect(self.open_folder)
        buttons_layout.addWidget(open_folder_btn)
        
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def get_history_file(self):
        """Ottiene il percorso del file della cronologia per l'anno corrente"""
        year = ordina_settings.current_settings["year"]
        history_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "Abe",
            "Ordina",
            year
        )
        os.makedirs(history_dir, exist_ok=True)
        return os.path.join(history_dir, f"cronologia_{year}.xlsx")
    
    def load_history(self):
        """Carica la cronologia dal file Excel"""
        try:
            if os.path.exists(self.history_file):
                df = pd.read_excel(self.history_file)
            else:
                df = pd.DataFrame(columns=["protocollo", "data", "ora", "file_path"])
                df.to_excel(self.history_file, index=False)
            
            self.populate_table(df)
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Errore",
                f"Errore nel caricamento della cronologia: {str(e)}"
            )
    
    def populate_table(self, df):
        """Popola la tabella con i dati del DataFrame"""
        self.table.setRowCount(len(df))
        
        for i, row in df.iterrows():
            items = [
                QTableWidgetItem(str(row['protocollo'])),
                QTableWidgetItem(str(row['data'])),
                QTableWidgetItem(str(row['ora'])),
                QTableWidgetItem(str(row['file_path']))
            ]
            
            for j, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, j, item)
    
    def search_protocol(self):
        """Filtra la tabella in base al testo cercato"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            row_visible = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
            self.table.setRowHidden(row, not row_visible)
    
    def open_file(self):
        """Apre il file selezionato"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            file_path = self.table.item(current_row, 3).text()
            if os.path.exists(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            else:
                QMessageBox.warning(
                    self,
                    "File non trovato",
                    f"Il file non esiste più nel percorso:\n{file_path}"
                )
    
    def open_folder(self):
        """Apre la cartella contenente il file"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            file_path = self.table.item(current_row, 3).text()
            folder_path = os.path.dirname(file_path)
            if os.path.exists(folder_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            else:
                QMessageBox.warning(
                    self,
                    "Cartella non trovata",
                    f"La cartella non esiste più nel percorso:\n{folder_path}"
                )

def add_to_history(protocol_number, file_path):
    """Aggiunge una nuova voce alla cronologia"""
    try:
        # Ottieni il file della cronologia
        year = ordina_settings.current_settings["year"]
        history_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "Abe",
            "Ordina",
            year
        )
        history_file = os.path.join(history_dir, f"cronologia_{year}.xlsx")
        
        # Crea o carica il DataFrame
        if os.path.exists(history_file):
            df = pd.read_excel(history_file)
        else:
            df = pd.DataFrame(columns=["protocollo", "data", "ora", "file_path"])
        
        # Aggiungi la nuova voce
        now = datetime.now()
        new_row = {
            "protocollo": protocol_number,
            "data": now.strftime("%d/%m/%Y"),
            "ora": now.strftime("%H:%M:%S"),
            "file_path": file_path
        }
        
        df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True)
        
        # Salva il DataFrame
        df.to_excel(history_file, index=False)
        
    except Exception as e:
        print(f"Errore nell'aggiunta alla cronologia: {e}") 
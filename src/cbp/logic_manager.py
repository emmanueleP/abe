import pandas as pd
import os
from datetime import datetime
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

class LogicManager:
    def __init__(self, gui):
        self.gui = gui
        self.df_entrate = None
        self.df_uscite = None
    
    def create_new_file(self):
        """Crea un nuovo file Excel con la struttura predefinita"""
        try:
            # Crea DataFrame vuoti con le colonne predefinite
            self.df_entrate = pd.DataFrame(columns=["Descrizione", "Importo", "Note"])
            self.df_uscite = pd.DataFrame(columns=["Descrizione", "Importo", "Note"])
            
            # Crea il file Excel con due fogli
            with pd.ExcelWriter(self.gui.file_path, engine='openpyxl') as writer:
                self.df_entrate.to_excel(writer, sheet_name='Entrate', index=False)
                self.df_uscite.to_excel(writer, sheet_name='Uscite', index=False)
            
            # Pulisci e prepara le tabelle
            self.setup_tables()
            
            # Aggiorna i totali
            self.gui.calculate_totals()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.gui,
                "Errore",
                f"Errore nella creazione del file: {str(e)}"
            )
            return False
    
    def load_file(self):
        """Carica i dati da un file Excel esistente"""
        try:
            # Leggi i fogli Excel
            self.df_entrate = pd.read_excel(self.gui.file_path, sheet_name='Entrate')
            self.df_uscite = pd.read_excel(self.gui.file_path, sheet_name='Uscite')
            
            # Carica i dati nelle tabelle
            self.setup_tables()
            
            # Aggiorna i totali
            self.gui.calculate_totals()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.gui,
                "Errore",
                f"Errore nel caricamento del file: {str(e)}"
            )
            return False
    
    def setup_tables(self):
        """Imposta le tabelle con i dati dei DataFrame"""
        # Configura tabella Entrate
        self.gui.entrate_table.setRowCount(max(20, len(self.df_entrate) + 5))
        self.populate_table(self.gui.entrate_table, self.df_entrate)
        
        # Configura tabella Uscite
        self.gui.uscite_table.setRowCount(max(20, len(self.df_uscite) + 5))
        self.populate_table(self.gui.uscite_table, self.df_uscite)
    
    def populate_table(self, table, df):
        """Popola una tabella con i dati di un DataFrame"""
        for i, row in df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value) if pd.notna(value) else "")
                table.setItem(i, j, item)
    
    def save_file(self):
        """Salva i dati correnti nel file Excel"""
        try:
            # Converti le tabelle in DataFrame
            self.df_entrate = self.table_to_df(self.gui.entrate_table)
            self.df_uscite = self.table_to_df(self.gui.uscite_table)
            
            # Salva nel file Excel
            with pd.ExcelWriter(self.gui.file_path, engine='openpyxl') as writer:
                self.df_entrate.to_excel(writer, sheet_name='Entrate', index=False)
                self.df_uscite.to_excel(writer, sheet_name='Uscite', index=False)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.gui,
                "Errore",
                f"Errore nel salvataggio del file: {str(e)}"
            )
            return False
    
    def table_to_df(self, table):
        """Converte una tabella in DataFrame"""
        data = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                value = item.text() if item else ""
                row_data.append(value)
            if any(row_data):  # Includi solo righe non vuote
                data.append(row_data)
        
        return pd.DataFrame(data, columns=[table.horizontalHeaderItem(i).text() 
                                         for i in range(table.columnCount())]) 
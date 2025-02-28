from PyQt5.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QAction, QDialog, QToolBar,
    QPushButton, QHeaderView
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from .models import AvisTableModel
from .excel_handler import import_from_excel, export_to_excel
from .settings import avis_settings as settings
from .startup_dialog import StartupDialog
import os
import pandas as pd
from ..utils import get_asset_path

class AvisGUI(QMainWindow):
    closed = pyqtSignal()  # Segnale emesso quando la finestra viene chiusa
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        
        # Mostra il dialogo di avvio
        startup = StartupDialog(self)
        if startup.exec_() == QDialog.Accepted and startup.file_path:
            self.file_path = startup.file_path
            
            # Imposta il titolo della finestra
            self.setWindowTitle(f"AViS66 - {os.path.basename(self.file_path)}")
            
            # Imposta le dimensioni della finestra
            self.resize(1400, 800)  # Dimensioni predefinite
            
            # Setup dell'interfaccia
            self.setup_ui()
            self.setup_menu()
            self.setup_toolbar()
            
            # Carica i dati
            if os.path.exists(self.file_path):
                self.load_data()
            else:
                self.create_new_file()
            
            # Applica il tema
            if self.app:
                self.apply_theme()
        else:
            # Se l'utente annulla, chiudi l'applicazione
            self.close()

        # Imposta l'icona
        self.setWindowIcon(QIcon(get_asset_path('logo_avis66.png')))

    def setup_toolbar(self):
        toolbar = self.addToolBar("Strumenti")
        
        # Pulsante Salva
        save_action = QAction(QIcon(os.path.join('src', 'assets', 'diskette.png')), "Salva", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Salva il registro")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        # Pulsante aggiungi riga con icona
        add_action = QAction(QIcon(os.path.join('src', 'assets', 'add.png')), 'Aggiungi Riga', self)
        add_action.setStatusTip('Aggiungi una nuova riga')
        add_action.triggered.connect(self.add_row)
        add_action.setShortcut('Ctrl+N')
        toolbar.addAction(add_action)

        # Separatore
        toolbar.addSeparator()

        # Pulsante elimina con icona
        delete_action = QAction(QIcon(os.path.join('src', 'assets', 'trash.png')), 'Elimina Riga', self)
        delete_action.setStatusTip('Elimina la riga selezionata')
        delete_action.triggered.connect(self.remove_row)
        delete_action.setShortcut('Del')
        toolbar.addAction(delete_action)

    def setup_ui(self):
        # Widget principale
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Tabella
        self.table_view = QTableView()
        self.table_model = AvisTableModel()
        self.table_view.setModel(self.table_model)
        
        # Impostazioni tabella
        header = self.table_view.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setDefaultAlignment(Qt.AlignLeft)
        
        # Stile tabella
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)
        self.table_view.verticalHeader().setDefaultSectionSize(30)
        
        # Imposta altezza minima intestazioni
        header.setMinimumHeight(40)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #2d5a53;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table_view)

    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        # Aggiungi riga
        add_action = QAction('Nuova Riga', self)
        add_action.triggered.connect(self.add_row)
        add_action.setShortcut('Ctrl+N')
        file_menu.addAction(add_action)
        
        import_action = QAction('Importa da Excel...', self)
        import_action.triggered.connect(self.import_excel)
        import_action.setShortcut('Ctrl+I')
        file_menu.addAction(import_action)
        
        export_action = QAction('Esporta in Excel...', self)
        export_action.triggered.connect(self.export_excel)
        export_action.setShortcut('Ctrl+E')
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Esci', self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(exit_action)
        
        # Menu Impostazioni
        settings_menu = menubar.addMenu('Impostazioni')
        settings_action = QAction('Configura...', self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)
        
        # Menu Help
        help_menu = menubar.addMenu('Help')
        about_action = QAction('Informazioni...', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importa da Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            try:
                data = import_from_excel(file_path)
                self.table_model.load_data(data)
                QMessageBox.information(self, "Successo", "Dati importati correttamente")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'importazione: {str(e)}")

    def export_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta in Excel",
            "",
            "Excel Files (*.xlsx)"
        )
        if file_path:
            try:
                export_to_excel(self.table_model.get_data(), file_path)
                QMessageBox.information(self, "Successo", "Dati esportati correttamente")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione: {str(e)}")

    def apply_theme(self):
        if self.app:
            from qt_material import apply_stylesheet
            theme = f"{settings.get_theme()}_teal.xml"
            apply_stylesheet(self.app, theme=theme)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept() 

    def add_row(self):
        """Aggiunge una nuova riga alla tabella"""
        current_row = self.table_view.currentIndex().row()
        position = current_row + 1 if current_row >= 0 else self.table_model.rowCount()
        self.table_model.insertRows(position, 1)
        
        # Seleziona la nuova riga
        index = self.table_model.index(position, 0)
        self.table_view.setCurrentIndex(index)
        self.table_view.edit(index)  # Inizia modifica della prima cella

    def remove_row(self):
        """Rimuove le righe selezionate"""
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        # Se è selezionata solo la prima riga (intestazione), non permettere l'eliminazione
        if len(selected_rows) == 1 and selected_rows[0].row() == 0:
            return
        
        # Rimuovi la prima riga dalla selezione se presente
        selected_rows = [row for row in selected_rows if row.row() > 0]
        if not selected_rows:
            return

        # Messaggio di conferma appropriato per singola o multiple righe
        if len(selected_rows) == 1:
            message = 'Sei sicuro di voler eliminare questa riga?'
        else:
            message = f'Sei sicuro di voler eliminare {len(selected_rows)} righe?'

        reply = QMessageBox.question(
            self,
            'Conferma eliminazione',
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Ordina gli indici in ordine decrescente per non alterare gli indici durante l'eliminazione
            rows = sorted([index.row() for index in selected_rows], reverse=True)
            for row in rows:
                self.table_model.removeRows(row, 1)
            
            QMessageBox.information(
                self,
                "Completato",
                "Righe eliminate con successo" if len(rows) > 1 else "Riga eliminata con successo"
            )

    def show_settings(self):
        from .settings import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_theme()

    def show_about(self):
        from .about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec_() 

    def save_file(self):
        """Salva il file Excel corrente"""
        try:
            if not hasattr(self, 'file_path') or not self.file_path:
                return
            
            # Salva i dati dalla tabella al DataFrame
            data = []
            model = self.table_view.model()
            for row in range(model.rowCount()):
                row_data = {}
                for col in range(model.columnCount()):
                    header = model.headerData(col, Qt.Horizontal)
                    index = model.index(row, col)
                    value = model.data(index)
                    row_data[header] = value if value is not None else ""
                data.append(row_data)
            
            # Crea DataFrame e salva
            df = pd.DataFrame(data)
            df.to_excel(self.file_path, index=False)
            
            self.statusBar().showMessage("File salvato con successo", 3000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore durante il salvataggio del file: {str(e)}"
            ) 

    def table_to_df(self):
        """Converte i dati della tabella in DataFrame"""
        data = []
        for row in range(self.table.rowCount()):
            row_data = {}
            for col in range(self.table.columnCount()):
                header = self.table.horizontalHeaderItem(col).text()
                item = self.table.item(row, col)
                value = item.text() if item else ""
                row_data[header] = value
            data.append(row_data)
        self.df = pd.DataFrame(data) 

    def create_new_file(self):
        """Crea un nuovo file Excel con le intestazioni predefinite"""
        try:
            # Crea un DataFrame vuoto con le colonne predefinite
            columns = settings.current_settings["column_names"].values()
            self.df = pd.DataFrame(columns=list(columns))
            
            # Salva il DataFrame nel nuovo file
            self.df.to_excel(self.file_path, index=False)
            
            # Carica i dati nella tabella
            self.table_model.load_data(self.df)
            
            self.statusBar().showMessage("Nuovo file creato con successo", 3000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nella creazione del nuovo file: {str(e)}"
            )
            self.close()

    def load_data(self):
        """Carica i dati dal file Excel esistente"""
        try:
            self.df = pd.read_excel(self.file_path)
            self.table_model.load_data(self.df)
            self.statusBar().showMessage("File caricato con successo", 3000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel caricamento del file: {str(e)}"
            )
            self.close() 
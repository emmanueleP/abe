from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QAction, QDialog, QComboBox, QHBoxLayout,
    QSpinBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from .file_handler import handle_file
from .settings import ordina_settings as settings, SettingsDialog
from .about_dialog import AboutDialog
import os
from io import BytesIO
from datetime import datetime
import json
from .database import ProtocolDatabase

class ProtocolGUI(QMainWindow):
    closed = pyqtSignal()
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("Ordina - Protocolla Documenti")
        self.setGeometry(200, 200, 800, 600)
        self.file_path = None
        self.protocol_button = None
        self.setup_menu()
        self.setup_ui()
        if self.app:
            self.apply_theme()

    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        load_action = QAction('Carica Documento...', self)
        load_action.triggered.connect(self.load_document)
        load_action.setShortcut('Ctrl+O')
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Esci', self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(exit_action)
        
        # Menu Strumenti
        tools_menu = menubar.addMenu('Strumenti')
        
        history_action = QAction('Cronologia Anno...', self)
        history_action.triggered.connect(self.show_history)
        tools_menu.addAction(history_action)

        reset_action = QAction('Azzera Numerazione...', self)
        reset_action.triggered.connect(self.reset_protocol)
        tools_menu.addAction(reset_action)
        
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

    def setup_ui(self):
        # Layout principale
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Gruppo Protocollo
        protocol_group = QGroupBox("Numerazione Protocollo")
        protocol_layout = QHBoxLayout()
        
        # Numero corrente
        current_number = settings.current_settings["last_protocol_number"] + 1
        self.protocol_label = QLabel(f"Prossimo numero: {current_number:05d}")
        protocol_layout.addWidget(self.protocol_label)
        
        protocol_group.setLayout(protocol_layout)
        layout.addWidget(protocol_group)
        
        # Preview
        preview_group = QGroupBox("Anteprima Documento")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Nessun documento caricato")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        self.upload_button = QPushButton("Carica Documento")
        self.upload_button.clicked.connect(self.load_document)
        buttons_layout.addWidget(self.upload_button)

        self.protocol_button = QPushButton("Protocolla")
        self.protocol_button.clicked.connect(self.protocol_document)
        self.protocol_button.setEnabled(False)
        buttons_layout.addWidget(self.protocol_button)
        
        layout.addLayout(buttons_layout)

    def load_document(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Seleziona Documento", 
                "", 
                "Documenti (*.pdf *.docx *.xlsx *.png *.jpg *.jpeg)"
            )
            if file_path:
                self.file_path = file_path
                if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                    pixmap = QPixmap(file_path)
                    self.preview_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
                else:
                    filename = os.path.basename(file_path)
                    self.preview_label.setText(f"File caricato: {filename}")
                    
                self.protocol_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento del file: {str(e)}")

    def protocol_document(self):
        if not self.file_path:
            QMessageBox.warning(self, "Attenzione", "Carica un documento prima di protocollare.")
            return

        try:
            result = handle_file(self.file_path)
            QMessageBox.information(self, "Successo", result)
            self.preview_label.setText(result)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la protocollazione: {str(e)}")

    def show_history(self):
        dialog = HistoryDialog(self)
        dialog.exec_()

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    def apply_theme(self):
        if self.app:
            from qt_material import apply_stylesheet
            theme = f"{settings.get_theme()}_teal.xml"
            apply_stylesheet(self.app, theme=theme)

    def reset_protocol(self):
        reply = QMessageBox.question(
            self,
            'Conferma Reset',
            'Vuoi davvero azzerare la numerazione per l\'anno corrente?\n'
            'Questa operazione non può essere annullata.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            settings.current_settings["last_protocol_number"] = 0
            settings.save_settings()
            current_number = settings.current_settings["last_protocol_number"] + 1
            self.protocol_label.setText(f"Prossimo numero: {current_number:05d}")
            QMessageBox.information(
                self,
                "Completato",
                "Numerazione azzerata con successo"
            )

    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_theme()
            current_number = settings.current_settings["last_protocol_number"] + 1
            self.protocol_label.setText(f"Prossimo numero: {current_number:05d}")

    def closeEvent(self, event):
        """Gestisce l'evento di chiusura della finestra"""
        self.closed.emit()  # Emette il segnale che farà riapparire la finestra di benvenuto
        event.accept()

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = ProtocolDatabase()
        self.setWindowTitle("Cronologia Protocolli")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Titolo e Ricerca
        header_layout = QHBoxLayout()
        
        title = QLabel("Cronologia Protocolli")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Campo di ricerca
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca...")
        self.search_input.textChanged.connect(self.search_history)
        header_layout.addWidget(self.search_input)
        
        layout.addLayout(header_layout)

        # Selezione Anno
        year_layout = QHBoxLayout()
        year_label = QLabel("Anno:")
        self.year_combo = QComboBox()
        self.year_combo.addItems(self.get_available_years())
        self.year_combo.currentTextChanged.connect(self.load_history)
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        layout.addLayout(year_layout)

        # Tabella cronologia
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Protocollo", "Data", "Ora", "Nome File", "Percorso"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.open_file)
        layout.addWidget(self.table)

        # Pulsanti azione
        buttons_layout = QHBoxLayout()
        
        open_file_btn = QPushButton("Apri File")
        open_file_btn.clicked.connect(self.open_file)
        buttons_layout.addWidget(open_file_btn)
        
        open_folder_btn = QPushButton("Apri Cartella")
        open_folder_btn.clicked.connect(self.open_folder)
        buttons_layout.addWidget(open_folder_btn)
        
        buttons_layout.addStretch()
        
        delete_button = QPushButton("Elimina Cronologia")
        delete_button.setStyleSheet("background-color: #ff4444; color: white;")
        delete_button.clicked.connect(self.delete_history)
        buttons_layout.addWidget(delete_button)
        
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def get_available_years(self):
        """Recupera gli anni disponibili dal database"""
        return self.db.get_available_years() or [str(datetime.now().year)]

    def load_history(self):
        """Carica la cronologia per l'anno selezionato"""
        try:
            self.table.clearContents()
            self.table.setRowCount(0)
            
            year = self.year_combo.currentText()
            entries = self.db.get_entries_by_year(year)
            
            self.table.setRowCount(len(entries))
            for i, entry in enumerate(entries):
                protocol, date, time, file_path = entry
                items = [
                    QTableWidgetItem(protocol),
                    QTableWidgetItem(date),
                    QTableWidgetItem(time),
                    QTableWidgetItem(os.path.basename(file_path)),
                    QTableWidgetItem(file_path)
                ]
                
                for col, item in enumerate(items):
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(i, col, item)
            
            # ... resto del codice per il formato della tabella ...
                    
        except Exception as e:
            print(f"Errore nel caricamento della cronologia: {e}")
            self.table.setRowCount(0)

    def delete_history(self):
        year = self.year_combo.currentText()
        reply = QMessageBox.question(
            self,
            'Conferma Eliminazione',
            f'Vuoi davvero eliminare la cronologia dell\'anno {year}?\n'
            'Questa operazione non può essere annullata.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_year(year)
                self.year_combo.clear()
                self.year_combo.addItems(self.get_available_years())
                self.load_history()
                QMessageBox.information(
                    self,
                    "Completato",
                    f"Cronologia dell'anno {year} eliminata con successo"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Errore durante l'eliminazione della cronologia: {str(e)}"
                )

    def search_history(self):
        """Cerca nella cronologia"""
        search_text = self.search_input.text().strip()
        if search_text:
            entries = self.db.search_entries(search_text)
            self.populate_table(entries)
        else:
            self.load_history()

    def populate_table(self, entries):
        """Popola la tabella con le voci"""
        self.table.clearContents()
        self.table.setRowCount(len(entries))
        
        for i, entry in enumerate(entries):
            protocol, date, time, file_path = entry
            items = [
                QTableWidgetItem(protocol),
                QTableWidgetItem(date),
                QTableWidgetItem(time),
                QTableWidgetItem(os.path.basename(file_path)),
                QTableWidgetItem(file_path)
            ]
            
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, col, item)
        
        # Seleziona la prima riga se presente
        if self.table.rowCount() > 0:
            self.table.selectRow(0)

    def open_file(self):
        """Apre il file selezionato"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            file_path = self.table.item(current_row, 4).text()
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
            file_path = self.table.item(current_row, 4).text()
            folder_path = os.path.dirname(file_path)
            if os.path.exists(folder_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            else:
                QMessageBox.warning(
                    self,
                    "Cartella non trovata",
                    f"La cartella non esiste più nel percorso:\n{folder_path}"
                )
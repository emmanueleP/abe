from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QAction, QDialog, QComboBox, QHBoxLayout,
    QSpinBox, QGroupBox
)
from PyQt5.QtGui import QPixmap, QDesktopServices, QIcon
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from .file_handler import handle_file
from .settings import ordina_settings as settings, SettingsDialog
from .about_dialog import AboutDialog
from .history_dialog import HistoryDialog
import os
from io import BytesIO
from datetime import datetime
import json
from ..utils import get_asset_path

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
        # Imposta l'icona
        self.setWindowIcon(QIcon(get_asset_path('logo_ordina.png')))

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
        """Mostra la finestra della cronologia"""
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
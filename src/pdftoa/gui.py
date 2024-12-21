from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QAction, QListWidget, QHBoxLayout,
    QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import fitz  # PyMuPDF
import os

class PDFtoAGUI(QMainWindow):
    closed = pyqtSignal()
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("PDFtoA - Conversione PDF in PDF/A")
        self.setGeometry(200, 200, 800, 600)
        self.setup_menu()
        self.setup_ui()
        self.pdf_files = []
        
        if self.app:
            self.apply_theme()

    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        load_action = QAction('Carica PDF...', self)
        load_action.triggered.connect(self.load_pdfs)
        load_action.setShortcut('Ctrl+O')
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Esci', self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(exit_action)
        
        # Menu Help
        help_menu = menubar.addMenu('Help')
        about_action = QAction('Informazioni...', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Lista dei file PDF
        files_group = QGroupBox("File PDF")
        files_layout = QVBoxLayout()
        
        self.files_list = QListWidget()
        files_layout.addWidget(self.files_list)
        
        # Pulsanti per la gestione dei file
        buttons_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Carica PDF")
        self.load_button.clicked.connect(self.load_pdfs)
        buttons_layout.addWidget(self.load_button)
        
        self.remove_button = QPushButton("Rimuovi")
        self.remove_button.clicked.connect(self.remove_selected)
        self.remove_button.setEnabled(False)
        buttons_layout.addWidget(self.remove_button)
        
        files_layout.addLayout(buttons_layout)
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)
        
        # Barra di progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Pulsante converti
        self.convert_button = QPushButton("Converti in PDF/A")
        self.convert_button.clicked.connect(self.convert_selected)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

    def load_pdfs(self):
        """Carica uno o più file PDF"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleziona PDF",
            "",
            "PDF Files (*.pdf)"
        )
        
        if files:
            for file_path in files:
                if file_path not in self.pdf_files:
                    self.pdf_files.append(file_path)
                    self.files_list.addItem(os.path.basename(file_path))
            
            self.update_buttons()

    def remove_selected(self):
        """Rimuove i file selezionati dalla lista"""
        for item in self.files_list.selectedItems():
            idx = self.files_list.row(item)
            self.files_list.takeItem(idx)
            del self.pdf_files[idx]
        
        self.update_buttons()

    def convert_selected(self):
        """Converte i file selezionati in PDF/A"""
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(selected_items))
        self.progress_bar.setValue(0)
        
        for i, item in enumerate(selected_items):
            idx = self.files_list.row(item)
            input_path = self.pdf_files[idx]
            
            try:
                # Crea il nome del file di output
                output_path = os.path.splitext(input_path)[0] + "_PDFA.pdf"
                
                # Converti in PDF/A
                doc = fitz.open(input_path)
                doc.convert_to_pdf_a()  # Converte in PDF/A
                doc.save(output_path)
                doc.close()
                
                self.progress_bar.setValue(i + 1)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Errore durante la conversione di {os.path.basename(input_path)}: {str(e)}"
                )
        
        self.progress_bar.setVisible(False)
        QMessageBox.information(
            self,
            "Completato",
            "Conversione completata con successo!"
        )

    def update_buttons(self):
        """Aggiorna lo stato dei pulsanti"""
        has_files = self.files_list.count() > 0
        has_selection = len(self.files_list.selectedItems()) > 0
        
        self.remove_button.setEnabled(has_selection)
        self.convert_button.setEnabled(has_selection)

    def show_about(self):
        from .about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec_()

    def apply_theme(self):
        if self.app:
            from qt_material import apply_stylesheet
            theme = "dark_teal.xml"
            apply_stylesheet(self.app, theme=theme)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept() 
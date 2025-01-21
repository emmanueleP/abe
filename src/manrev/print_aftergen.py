import win32com.client
import win32print
import time
import os
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel

class PrinterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Stampante")
        self.setFixedSize(200, 200)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Lista stampanti
        self.printer_combo = QComboBox()
        self.printer_combo.addItems(self.get_printers())
        
        # Imposta stampante predefinita come selezionata
        default_printer = win32print.GetDefaultPrinter()
        index = self.printer_combo.findText(default_printer)
        if index >= 0:
            self.printer_combo.setCurrentIndex(index)
            
        layout.addWidget(QLabel("Seleziona stampante:"))
        layout.addWidget(self.printer_combo)
        
        # Pulsanti
        print_btn = QPushButton("Stampa")
        print_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        
        layout.addWidget(print_btn)
        layout.addWidget(cancel_btn)
        
        self.setLayout(layout)
    
    def get_printers(self):
        printers = []
        for printer in win32print.EnumPrinters(2):
            printers.append(printer[2])
        return printers
    
    def selected_printer(self):
        return self.printer_combo.currentText()

class PrintManager:
    def __init__(self):
        self.word_app = None
        
    def print_document(self, file_path, parent=None):
        """Stampa un documento Word"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File non trovato: {file_path}")
            
            # Mostra dialog selezione stampante
            printer_dialog = PrinterDialog(parent)
            if printer_dialog.exec_() != QDialog.Accepted:
                return False
                
            selected_printer = printer_dialog.selected_printer()
            
            # Inizializza Word
            self.word_app = win32com.client.Dispatch("Word.Application")
            self.word_app.Visible = False
            
            # Apri il documento
            doc = self.word_app.Documents.Open(os.path.abspath(file_path))
            
            # Imposta la stampante selezionata
            self.word_app.ActivePrinter = selected_printer
            
            # Stampa
            doc.PrintOut(Background=False)
            
            # Attendi il completamento della stampa
            time.sleep(2)
            
            # Chiudi il documento
            doc.Close()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Errore di stampa",
                f"Errore durante la stampa: {str(e)}"
            )
            return False
            
        finally:
            if self.word_app:
                try:
                    self.word_app.Quit()
                except:
                    pass
                self.word_app = None

# Istanza singleton del gestore stampe
print_manager = PrintManager() 
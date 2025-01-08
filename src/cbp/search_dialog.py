from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel
)
from PyQt5.QtCore import Qt

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cerca")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Campo di ricerca
        search_layout = QHBoxLayout()
        self.search_text = QLineEdit()
        self.search_text.setPlaceholderText("Inserisci il testo da cercare...")
        self.search_text.returnPressed.connect(self.accept)
        search_layout.addWidget(self.search_text)
        
        search_btn = QPushButton("Cerca")
        search_btn.clicked.connect(self.accept)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Info
        info = QLabel("La ricerca verrà effettuata su tutte le colonne")
        info.setStyleSheet("color: gray;")
        layout.addWidget(info)
        
        self.setLayout(layout) 
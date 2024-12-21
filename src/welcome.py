from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel,
    QWidget, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.ordina.gui import ProtocolGUI
from src.avis66.gui import AvisGUI

class WelcomeDialog(QDialog):
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("Abe-Gestionale")
        self.setFixedSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Titolo
        title = QLabel("Benvenuto in Abe-Gestionale")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Bold))
        layout.addWidget(title)

        # Sottotitolo
        subtitle = QLabel("Seleziona l'applicazione da avviare")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont('Arial', 12))
        layout.addWidget(subtitle)

        # Container per i pulsanti
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_container.setLayout(buttons_layout)

        # Pulsante Ordina
        ordina_button = self.create_app_button(
            "Ordina",
            "Gestione protocollo documenti",
            self.launch_ordina
        )
        buttons_layout.addWidget(ordina_button)

        # Pulsante AViS66
        avis_button = self.create_app_button(
            "AViS66",
            "Gestione Avis",
            self.launch_avis
        )
        buttons_layout.addWidget(avis_button)

        layout.addWidget(buttons_container)

        # Copyright
        copyright = QLabel("© 2024 Emmanuele Pani. Under MIT License.")
        copyright.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright)

        self.setLayout(layout)

    def create_app_button(self, title, description, callback):
        button = QPushButton()
        button.setMinimumSize(250, 200)
        button.setStyleSheet("""
            QPushButton {
                border: 2px solid #2196F3;
                border-radius: 10px;
                padding: 20px;
                background-color: #E3F2FD;
            }
            QPushButton:hover {
                background-color: #BBDEFB;
            }
        """)

        # Layout interno del pulsante
        button_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        button_layout.addWidget(title_label)
        button_layout.addWidget(desc_label)
        button.setLayout(button_layout)
        
        button.clicked.connect(callback)
        return button

    def launch_ordina(self):
        self.hide()
        self.ordina_window = ProtocolGUI(self.app)
        self.ordina_window.show()
        self.ordina_window.closed.connect(self.show)

    def launch_avis(self):
        try:
            self.hide()
            self.avis_window = AvisGUI(self.app)
            self.avis_window.show()
            self.avis_window.closed.connect(self.show)
        except Exception as e:
            print(f"Errore: {e}")  # Per debug
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'avvio di AViS66: {str(e)}"
            )
            self.show()
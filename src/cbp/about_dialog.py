from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informazioni")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Logo o titolo
        title = QLabel("CBP")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Versione
        version = QLabel("Versione 1.0.5")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # Descrizione
        description = QLabel(
            "Gestione registro banca, cassa e carta prepagata.\n"
            "Permette di gestire l'archivio della contabilità con funzionalità "
            "tipiche di un file Entrate/Uscite."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignJustify)
        layout.addWidget(description)

        # Copyright
        copyright = QLabel("© 2025 - Emmanuele Pani. Under MIT License.")
        copyright.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright)

        # Pulsante chiudi
        close_button = QPushButton("Chiudi")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout) 
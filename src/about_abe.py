from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informazioni su Abe-Gestionale")
        self.setFixedSize(600, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Tab widget per organizzare le informazioni
        tab_widget = QTabWidget()
        
        # Tab Generale
        general_tab = QLabel()
        general_tab.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        general_tab.setWordWrap(True)
        general_tab.setText(
            "<h2>Abe-Gestionale v1.0.1</h2>"
            "<p>Suite di applicazioni per la gestione della segreteria di una sede Avis.</p>"
            "<h3>Applicazioni:</h3>"
            "<ul>"
            "<li><b>📝 Ordina:</b> Protocollazione documenti</li>"
            "<li><b>👥 aViS66:</b> Gestione Libro Soci Avis</li>"
            "<li><b>📄 PDFtoA:</b> Conversione PDF in PDF/A</li>"
            "<li><b>💰 ManRev:</b> Gestione Mandati e Reversali</li>"
            "<li><b>📊 CBP:</b> Gestione Rendiconto per cassa</li>"
            "<li><b>📅 Agenda:</b> Gestione eventi e promemoria</li>"
            "</ul>"
        )
        tab_widget.addTab(general_tab, "Generale")
        
        # Tab Licenza
        license_tab = QLabel()
        license_tab.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        license_tab.setWordWrap(True)
        license_tab.setText(
            "<h3>MIT License</h3>"
            "<p>Copyright (c) 2025 Emmanuele Pani</p>"
            "<p>Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files (the \"Software\"), to deal "
            "in the Software without restriction, including without limitation the rights "
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            "copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:</p>"
            "<p>The above copyright notice and this permission notice shall be included in all "
            "copies or substantial portions of the Software.</p>"
        )
        tab_widget.addTab(license_tab, "Licenza")
        
        # Tab Contatti
        contacts_tab = QLabel()
        contacts_tab.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        contacts_tab.setWordWrap(True)
        contacts_tab.setText(
            "<h3>Contatti</h3>"
            "<p><b>Developed by:</b> Emmanuele Pani</p>"
            "<p><b>GitHub:</b> github.com/emmanueleP</p>"
            "<h3>Report Bug</h3>"
            "<p>Per segnalare problemi o suggerire miglioramenti, "
            "apri una issue su GitHub.</p>"
        )
        tab_widget.addTab(contacts_tab, "Contatti")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout) 
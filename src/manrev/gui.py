from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QAction, QHBoxLayout, QGroupBox,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QCheckBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from .settings import manrev_settings
from .generator import generate_documents
from .about_dialog import AboutDialog

class ManRevGUI(QMainWindow):
    closed = pyqtSignal()
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("ManRev - Gestione Mandati e Reversali")
        self.setGeometry(200, 200, 800, 600)
        self.setup_menu()
        self.setup_ui()
        
        if self.app:
            self.apply_theme()

    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        generate_action = QAction('Genera Documento...', self)
        generate_action.triggered.connect(self.generate_document)
        generate_action.setShortcut('Ctrl+G')
        file_menu.addAction(generate_action)
        
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

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Gruppo Tipo Documento
        doc_group = QGroupBox("Tipo Documento")
        doc_layout = QHBoxLayout()
        
        self.doc_type = QComboBox()
        self.doc_type.addItems(["Mandato di Pagamento", "Reversale di Esazione"])
        doc_layout.addWidget(self.doc_type)
        
        doc_group.setLayout(doc_layout)
        layout.addWidget(doc_group)
        
        # Gruppo Informazioni Documento
        info_group = QGroupBox("Informazioni Documento")
        info_layout = QVBoxLayout()
        
        # Numero
        num_row = QHBoxLayout()
        num_row.addWidget(QLabel("Numero:"))
        self.number_input = QLineEdit()
        num_row.addWidget(self.number_input)
        info_layout.addLayout(num_row)
        
        # Capitolo
        cap_row = QHBoxLayout()
        cap_row.addWidget(QLabel("Capitolo:"))
        self.chapter_input = QComboBox()
        self.chapter_input.setEditable(True)
        self.chapter_input.addItems(manrev_settings.current_settings.get("capitoli", []))
        self.chapter_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        cap_row.addWidget(self.chapter_input)
        info_layout.addLayout(cap_row)
        
        # Importo
        amount_row = QHBoxLayout()
        amount_row.addWidget(QLabel("Importo €:"))
        self.amount_input = QLineEdit()
        amount_row.addWidget(self.amount_input)
        info_layout.addLayout(amount_row)
        
        # Descrizione
        desc_row = QHBoxLayout()
        desc_row.addWidget(QLabel("Descrizione:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        desc_row.addWidget(self.description_input)
        info_layout.addLayout(desc_row)
        
        # Data e Luogo
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Data:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        date_row.addWidget(self.date_input)
        
        date_row.addWidget(QLabel("Luogo:"))
        self.place_input = QLineEdit()
        self.place_input.setText(manrev_settings.current_settings.get("default_place", ""))
        date_row.addWidget(self.place_input)
        info_layout.addLayout(date_row)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Gruppo Firme
        sign_group = QGroupBox("Firme")
        sign_layout = QVBoxLayout()
        
        # Tesoriere
        tres_row = QHBoxLayout()
        tres_row.addWidget(QLabel("Il Tesoriere:"))
        self.treasurer_input = QLineEdit()
        self.treasurer_input.setText(manrev_settings.current_settings.get("default_treasurer", ""))
        tres_row.addWidget(self.treasurer_input)
        sign_layout.addLayout(tres_row)
        
        # Presidente
        pres_row = QHBoxLayout()
        pres_row.addWidget(QLabel("Il Presidente:"))
        self.president_input = QLineEdit()
        self.president_input.setText(manrev_settings.current_settings.get("default_president", ""))
        pres_row.addWidget(self.president_input)
        sign_layout.addLayout(pres_row)
        
        # Addetto Contabile
        acc_row = QHBoxLayout()
        acc_row.addWidget(QLabel("L'Addetto Contabile:"))
        self.accountant_input = QLineEdit()
        self.accountant_input.setText(manrev_settings.current_settings.get("default_accountant", ""))
        acc_row.addWidget(self.accountant_input)
        sign_layout.addLayout(acc_row)
        
        sign_group.setLayout(sign_layout)
        layout.addWidget(sign_group)
        
        # Opzioni
        options_layout = QHBoxLayout()
        self.print_check = QCheckBox("Stampa dopo la generazione")
        options_layout.addWidget(self.print_check)
        layout.addLayout(options_layout)
        
        # Pulsante genera
        self.generate_button = QPushButton("Genera Documento")
        self.generate_button.clicked.connect(self.generate_document)
        layout.addWidget(self.generate_button)

    def generate_document(self):
        """Avvia la generazione del documento"""
        from .generator import generate_document
        generate_document(self)

    def show_settings(self):
        from .settings import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Aggiorna i valori predefiniti
            self.place_input.setText(manrev_settings.current_settings["default_place"])
            self.treasurer_input.setText(manrev_settings.current_settings["default_treasurer"])
            self.president_input.setText(manrev_settings.current_settings["default_president"])
            self.accountant_input.setText(manrev_settings.current_settings["default_accountant"])
            # Aggiorna la lista dei capitoli
            self.chapter_input.clear()
            self.chapter_input.addItems(manrev_settings.current_settings.get("capitoli", []))

    def show_about(self):
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

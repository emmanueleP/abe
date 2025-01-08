from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QLabel,
    QWidget, QHBoxLayout, QMessageBox, QMenuBar, QMenu, QAction, QActionGroup
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from src.ordina.gui import ProtocolGUI
from src.avis66.gui import AvisGUI
from src.pdftoa.gui import PDFtoAGUI
from src.manrev.gui import ManRevGUI
from src.cbp.gui import CbpGUI
from src.updater import UpdateSettings, UpdateChecker, UpdateDialog
import json

class WelcomeDialog(QMainWindow):
    closed = pyqtSignal()
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("Abe-Gestionale")
        self.setFixedSize(1400, 900)
        self.setup_menu()
        self.setup_ui()
        
        # Controlla aggiornamenti all'avvio se abilitato
        self.check_updates_on_startup()

    def setup_menu(self):
        menubar = QMenuBar()
        self.setMenuBar(menubar)
        
        # Menu Impostazioni
        settings_menu = menubar.addMenu('Impostazioni')
        
        # Sottomenu Tema
        theme_menu = QMenu('Tema', self)
        settings_menu.addMenu(theme_menu)
        
        # Azioni per i temi
        light_action = QAction('Chiaro', self)
        light_action.setCheckable(True)
        light_action.triggered.connect(lambda: self.change_theme('light'))
        
        dark_action = QAction('Scuro', self)
        dark_action.setCheckable(True)
        dark_action.setChecked(True)  # Tema scuro predefinito
        dark_action.triggered.connect(lambda: self.change_theme('dark'))
        
        # Aggiungi le azioni al gruppo per renderle mutuamente esclusive
        theme_group = QActionGroup(self)
        theme_group.addAction(light_action)
        theme_group.addAction(dark_action)
        theme_group.setExclusive(True)
        
        theme_menu.addAction(light_action)
        theme_menu.addAction(dark_action)
        
        # Aggiornamenti
        update_action = QAction('Aggiornamenti...', self)
        update_action.triggered.connect(self.show_update_settings)
        settings_menu.addAction(update_action)
        
        # Menu Help
        help_menu = menubar.addMenu('Help')
        
        manual_action = QAction('Manuale', self)
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('Informazioni', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def change_theme(self, theme):
        """Cambia il tema dell'applicazione"""
        try:
            from qt_material import apply_stylesheet
            theme_file = f"{theme}_teal.xml"
            apply_stylesheet(self.app, theme=theme_file)
            
            # Salva il tema nelle impostazioni
            with open('data/config/config.json', 'r+') as f:
                config = json.load(f)
                config['theme'] = theme
                f.seek(0)
                json.dump(config, f, indent=4)
                f.truncate()
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel cambio tema: {str(e)}")

    def show_manual(self):
        """Mostra il manuale dell'applicazione"""
        QMessageBox.information(
            self,
            "Manuale",
            "Il manuale dell'applicazione sarà disponibile prossimamente."
        )

    def show_about(self):
        """Mostra informazioni sull'applicazione"""
        QMessageBox.about(
            self,
            "Informazioni",
            "Abe-Gestionale v1.0.0\n\n"
            "Suite di applicazioni per la gestione della segreteria di una sede Avis.\n\n"
            "- Ordina: Protocollazione documenti\n"
            "- aViS66: Gestione Libro Soci Avis\n"
            "- PDFtoA: Conversione PDF in PDF/A\n"
            "- ManRev: Gestione Mandati e Reversali Avis\n\n"
            "© 2025 Emmanuele Pani\n"
            "Under MIT License"
        )

    def setup_ui(self):
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)

        # Titolo
        title = QLabel("Benvenuto in Abe-Gestionale")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Bold))
        main_layout.addWidget(title)

        # Sottotitolo
        subtitle = QLabel("Seleziona l'applicazione da avviare")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont('Arial', 12))
        main_layout.addWidget(subtitle)

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
            "aViS66",
            "Gestione Libro Soci Avis",
            self.launch_avis
        )
        buttons_layout.addWidget(avis_button)

        # Pulsante PDFtoA
        pdftoa_button = self.create_app_button(
            "PDFtoA",
            "Conversione PDF in PDF/A",
            self.launch_pdftoa
        )
        buttons_layout.addWidget(pdftoa_button)

        # Pulsante ManRev
        manrev_button = self.create_app_button(
            "ManRev",
            "Gestione Mandati e Reversali Avis",
            self.launch_manrev
        )
        buttons_layout.addWidget(manrev_button)

        # Pulsante CBP
        cbp_button = self.create_app_button(
            "CBP",
            "Gestione Rendiconto per cassa",
            self.launch_cbp
        )
        buttons_layout.addWidget(cbp_button)

        main_layout.addWidget(buttons_container)

        # Copyright
        copyright = QLabel("© 2025 Emmanuele Pani. Under MIT License.")
        copyright.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright)

    def create_app_button(self, title, description, callback):
        button = QPushButton()
        button.setMinimumSize(250, 200)
        button.setStyleSheet("""
            QPushButton {
                border: 2px solid #2196F3;
                border-radius: 10px;
                padding: 20px;
                background-color: #33cccc;
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

    def launch_pdftoa(self):
        try:
            self.hide()
            self.pdftoa_window = PDFtoAGUI(self.app)
            self.pdftoa_window.show()
            self.pdftoa_window.closed.connect(self.show)
        except Exception as e:
            print(f"Errore: {e}")  # Per debug
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'avvio di PDFtoA: {str(e)}"
            )
            self.show()

    def launch_manrev(self):
        try:
            self.hide()
            self.manrev_window = ManRevGUI(self.app)
            self.manrev_window.show()
            self.manrev_window.closed.connect(self.show)
        except Exception as e:
            print(f"Errore: {e}")  # Per debug
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'avvio di ManRev: {str(e)}"
            )
            self.show()

    def launch_cbp(self):
        self.hide()
        self.cbp_window = CbpGUI(self.app)
        self.cbp_window.show()
        self.cbp_window.closed.connect(self.show)

    def closeEvent(self, event):
        if hasattr(self, 'update_checker'):
            self.update_checker.stop()
        self.closed.emit()
        event.accept()

    def show_update_settings(self):
        dialog = UpdateSettings(self)
        dialog.exec_()

    def check_updates_on_startup(self):
        try:
            with open('data/config/config.json', 'r') as f:
                config = json.load(f)
                if config.get('updates', {}).get('auto_check', True):
                    self.update_checker = UpdateChecker("1.0.0")  # Mantieni il riferimento
                    self.update_checker.update_available.connect(self.show_update_available)
                    self.update_checker.error_occurred.connect(lambda e: print(f"Errore aggiornamenti: {e}"))
                    self.update_checker.start()
        except Exception as e:
            print(f"Errore nel controllo aggiornamenti: {e}")

    def show_update_available(self, version, release_notes):
        dialog = UpdateDialog(self, version, release_notes)
        dialog.exec_()
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QLabel,
    QWidget, QHBoxLayout, QMessageBox, QMenuBar, QMenu, QAction, QActionGroup, QTabWidget, QDialog, QSpacerItem, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from src.ordina.gui import ProtocolGUI
from src.avis66.gui import AvisGUI
from src.pdftoa.gui import PDFtoAGUI
from src.manrev.gui import ManRevGUI
from src.cbp.gui import CbpGUI
from src.agenda.gui import AgendaGUI
from src.updater import UpdateSettings, UpdateChecker, UpdateDialog
from .about_abe import AboutDialog
from .manual_abe import ManualDialog
from .utils import get_asset_path
import json
import os

class WelcomeDialog(QMainWindow):
    closed = pyqtSignal()
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("Abe-Gestionale")
        self.setBaseSize(1080, 720)
        self.update_checker = None  
        self.center()
        self.setup_menu()
        self.setup_ui()
        
        # Controlla aggiornamenti all'avvio se abilitato
        self.check_updates_on_startup()
    # Centra la finestra all'apertura
    def showEvent(self, event):
        self.center()
        super().showEvent(event)
    
    def center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.frameGeometry()
         # Calcola la posizione centrale
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2

        # Imposta la posizione
        self.move(x, y)

    # Imposta l'icona dell'applicazione
        icon_path = os.path.join("src", "assets", "logo_abe.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            if self.app:
                self.app.setWindowIcon(QIcon(icon_path))
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
        dialog = ManualDialog(self)
        dialog.exec_()

    def show_about(self):
        """Mostra informazioni sull'applicazione"""
        dialog = AboutDialog(self)
        dialog.exec_()

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

        # Logo
        logo_label = QLabel()
        logo_path = get_asset_path('logo_abe.png')
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_pixmap = logo_pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(logo_label)

        # Sottotitolo
        subtitle = QLabel("Seleziona l'applicazione da avviare. Puoi tornare qui da qualsiasi app cliccando su Ctrl+Q")
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

        # Pulsante Agenda
        agenda_button = self.create_app_button(
            "Agenda",
            "Gestione calendario e appuntamenti",
            self.launch_agenda
        )
        buttons_layout.addWidget(agenda_button)

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
        
        # Titolo sopra
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(title_label)
        
        # Logo al centro
        logo_label = QLabel()
        logo_path = get_asset_path(f'logo_{title.lower()}.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(logo_label)
        
        # Descrizione sotto
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
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

    def launch_agenda(self):
        """Avvia l'applicazione Agenda"""
        from .agenda import AgendaGUI
        self.hide()
        self.current_app = AgendaGUI(self.app)
        self.current_app.closed.connect(self.show)
        self.current_app.show()

    def closeEvent(self, event):
        """Gestisce la chiusura della finestra"""
        if self.update_checker is not None:
            try:
                # Disconnetti i segnali
                self.update_checker.update_available.disconnect()
                self.update_checker.error_occurred.disconnect()
                
                # Imposta il flag di stop
                self.update_checker.stop_requested = True
                
                # Termina il thread in modo sicuro
                self.update_checker.quit()
                self.update_checker = None
                
            except Exception as e:
                print(f"Errore durante la chiusura del thread dell'updater: {e}")
        
        event.accept()

    def show_update_settings(self):
        dialog = UpdateSettings(self)
        dialog.exec_()

    def check_updates_on_startup(self):
        """Controlla gli aggiornamenti all'avvio"""
        try:
            # Verifica che non ci sia già un update_checker attivo
            if self.update_checker is not None:
                return
                
            with open('data/config/config.json', 'r') as f:
                config = json.load(f)
                if config.get('updates', {}).get('auto_check', True):
                    self.update_checker = UpdateChecker("1.0.0")
                    self.update_checker.update_available.connect(self.show_update_available)
                    self.update_checker.error_occurred.connect(
                        lambda e: print(f"Errore aggiornamenti: {e}")
                    )
                    self.update_checker.start()
        except Exception as e:
            print(f"Errore nel controllo aggiornamenti: {e}")

    def show_update_available(self, version, release_notes):
        """Mostra il dialog degli aggiornamenti disponibili"""
        # Verifica che il dialog non sia già aperto
        if not hasattr(self, 'update_dialog') or not self.update_dialog.isVisible():
            self.update_dialog = UpdateDialog(self, version, release_notes)
            self.update_dialog.exec_()
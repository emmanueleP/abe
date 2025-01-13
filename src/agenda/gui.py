from PyQt5.QtWidgets import (
    QMainWindow, QCalendarWidget, QVBoxLayout, QWidget,
    QPushButton, QLabel, QMessageBox, QHBoxLayout, QListWidget,
    QMenuBar, QMenu, QAction, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime, QTimer
from datetime import datetime, timedelta
from win10toast import ToastNotifier
from .database import AgendaDB
from .event_dialog import EventDialog
from PyQt5.QtGui import QTextCharFormat, QColor, QIcon
from .settings import SettingsDialog, agenda_settings
from ..utils import get_asset_path

class AgendaGUI(QMainWindow):
    closed = pyqtSignal()
    
    def __init__(self, app=None):
        super().__init__()
        self.setWindowIcon(QIcon(get_asset_path('logo_agenda.png')))
        self.app = app
        self.setWindowTitle("Agenda")
        self.setGeometry(100, 100, 800, 600)
        self.db = AgendaDB()
        self.toaster = ToastNotifier()
        self.setup_menu()
        self.setup_ui()
        self.setup_notifications()
        self.highlight_days_with_events()
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        new_event = QAction('Nuovo Evento...', self)
        new_event.triggered.connect(self.add_event)
        new_event.setShortcut('Ctrl+N')
        file_menu.addAction(new_event)
        
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
        
        # Menu Visualizza
        view_menu = menubar.addMenu('Visualizza')
        
        refresh_action = QAction('Aggiorna', self)
        refresh_action.triggered.connect(self.update_events_list)
        refresh_action.setShortcut('F5')
        view_menu.addAction(refresh_action)
        
        # Menu Help
        help_menu = menubar.addMenu('Help')
        about_action = QAction('Informazioni...', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        
    def setup_notifications(self):
        """Configura il timer per le notifiche"""
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_notifications)
        self.notification_timer.start(60000)  # Controlla ogni minuto
        
    def check_notifications(self):
        """Controlla e invia notifiche per gli eventi imminenti"""
        current_time = datetime.now()
        current_day = current_time.day
        
        events = self.db.get_events(current_day)
        for event in events:
            if not event[7]:  # Se notify è False
                continue
                
            event_time = datetime.strptime(event[4], "%H:%M").time()
            event_datetime = datetime.combine(current_time.date(), event_time)
            notify_before = timedelta(minutes=event[8])  # notify_minutes
            
            if current_time + notify_before >= event_datetime:
                self.toaster.show_toast(
                    "Promemoria Evento",
                    f"{event[2]}\n{event[3]}",
                    duration=10,
                    threaded=True
                )
    
    def show_about(self):
        from .about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec_()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Calendario
        calendar_container = QWidget()
        calendar_layout = QVBoxLayout(calendar_container)
        
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.day_clicked)
        calendar_layout.addWidget(self.calendar)
        
        layout.addWidget(calendar_container)
        
        # Lista eventi
        events_container = QWidget()
        events_layout = QVBoxLayout(events_container)
        
        self.events_list = QListWidget()
        self.events_list.itemDoubleClicked.connect(self.edit_event)
        events_layout.addWidget(self.events_list)
        
        add_button = QPushButton("Aggiungi Evento")
        add_button.clicked.connect(self.add_event)
        events_layout.addWidget(add_button)
        
        layout.addWidget(events_container)
        
        # Aggiorna la lista eventi per il giorno corrente
        self.update_events_list()
    
    def day_clicked(self, date):
        self.update_events_list(date.day())
        self.highlight_days_with_events()  # Aggiorna l'evidenziazione
    
    def update_events_list(self, day=None):
        if day is None:
            day = self.calendar.selectedDate().day()
            
        self.events_list.clear()
        events = self.db.get_events(day)
        
        for event in events:
            time_str = f"[{event[4]}] " if event[4] else ""
            self.events_list.addItem(f"{time_str}{event[2]}")
    
    def add_event(self):
        dialog = EventDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            day = self.calendar.selectedDate().day()
            self.db.add_event(
                day=day,
                title=dialog.title_input.text(),
                description=dialog.desc_input.toPlainText(),
                time=dialog.time_input.time().toString("HH:mm"),
                category=dialog.category_input.currentText(),
                priority=dialog.priority_input.value()
            )
            self.update_events_list()
    
    def edit_event(self, item):
        day = self.calendar.selectedDate().day()
        events = self.db.get_events(day)
        event = events[self.events_list.row(item)]
        
        dialog = EventDialog(self, event)
        if dialog.exec_() == QDialog.Accepted:
            self.db.update_event(
                event[0],
                title=dialog.title_input.text(),
                description=dialog.desc_input.toPlainText(),
                time=dialog.time_input.time().toString("HH:mm"),
                category=dialog.category_input.currentText(),
                priority=dialog.priority_input.value()
            )
            self.update_events_list()
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept() 
    
    def highlight_days_with_events(self):
        """Evidenzia i giorni che hanno eventi"""
        # Reset formato precedente
        format = self.calendar.dateTextFormat()
        for day in range(1, 32):
            self.calendar.setDateTextFormat(
                QDate(self.calendar.yearShown(), 
                      self.calendar.monthShown(), 
                      day),
                QTextCharFormat()
            )
        
        # Evidenzia i giorni con eventi
        events = self.db.get_events()
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 200, 200))  # Rosso chiaro
        
        for event in events:
            date = QDate(self.calendar.yearShown(),
                        self.calendar.monthShown(),
                        event[1])  # event[1] è il giorno
            self.calendar.setDateTextFormat(date, highlight_format)

    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Aggiorna le categorie nel dialog degli eventi
            self.update_categories()

    def update_categories(self):
        """Aggiorna la lista delle categorie disponibili"""
        categories = agenda_settings.current_settings["categories"]
        # Aggiorna tutte le istanze aperte di EventDialog se necessario

    def update_categories(self):
        """Aggiorna la lista delle categorie disponibili"""
        categories = agenda_settings.current_settings["categories"]
        # Aggiorna tutte le istanze aperte di EventDialog se necessario

    def update_categories(self):
        """Aggiorna la lista delle categorie disponibili"""
        categories = agenda_settings.current_settings["categories"]
        # Aggiorna tutte le istanze aperte di EventDialog se necessario 
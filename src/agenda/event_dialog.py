from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QTimeEdit,
    QCheckBox
)
from PyQt5.QtCore import Qt, QTime
from .settings import agenda_settings

class EventDialog(QDialog):
    def __init__(self, parent=None, event_data=None):
        super().__init__(parent)
        self.event_data = event_data
        self.setWindowTitle("Evento")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Titolo
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Titolo evento")
        layout.addWidget(self.title_input)
        
        # Ora
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Ora:"))
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.time_input)
        layout.addLayout(time_layout)
        
        # Notifica
        notify_layout = QHBoxLayout()
        self.notify_check = QCheckBox("Notifica")
        notify_layout.addWidget(self.notify_check)
        self.notify_before = QSpinBox()
        self.notify_before.setRange(0, 60)
        self.notify_before.setValue(15)
        notify_layout.addWidget(self.notify_before)
        notify_layout.addWidget(QLabel("minuti prima"))
        layout.addLayout(notify_layout)
        
        # Descrizione
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descrizione")
        layout.addWidget(self.desc_input)
        
        # Categoria
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Categoria:"))
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(agenda_settings.current_settings["categories"])
        cat_layout.addWidget(self.category_input)
        layout.addLayout(cat_layout)
        
        # Priorità
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Priorità:"))
        self.priority_input = QSpinBox()
        self.priority_input.setRange(0, 5)
        priority_layout.addWidget(self.priority_input)
        layout.addLayout(priority_layout)
        
        # Pulsanti
        buttons = QHBoxLayout()
        save_btn = QPushButton("Salva")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        if self.event_data:
            self.title_input.setText(self.event_data[2])
            if self.event_data[4]:
                self.time_input.setTime(QTime.fromString(self.event_data[4], "HH:mm"))
            self.desc_input.setText(self.event_data[3])
            self.category_input.setCurrentText(self.event_data[5])
            self.priority_input.setValue(self.event_data[6])
            self.notify_check.setChecked(bool(self.event_data[7]))
            
        self.setLayout(layout) 
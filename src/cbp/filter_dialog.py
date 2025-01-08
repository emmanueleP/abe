from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QCheckBox, QTabWidget, QListWidgetItem, QWidget
)
from PyQt5.QtCore import Qt

class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Filtri")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Tab per Entrate e Uscite
        tab_widget = QTabWidget()
        
        # Tab Entrate
        entrate_tab = QWidget()
        entrate_layout = QVBoxLayout()
        entrate_layout.addWidget(QLabel("Filtra per Descrizione:"))
        
        # Lista valori unici per Entrate
        self.entrate_list = QListWidget()
        self.populate_filter_list(self.parent.entrate_table, 0, self.entrate_list)
        entrate_layout.addWidget(self.entrate_list)
        
        entrate_tab.setLayout(entrate_layout)
        tab_widget.addTab(entrate_tab, "Entrate")
        
        # Tab Uscite
        uscite_tab = QWidget()
        uscite_layout = QVBoxLayout()
        uscite_layout.addWidget(QLabel("Filtra per Descrizione:"))
        
        # Lista valori unici per Uscite
        self.uscite_list = QListWidget()
        self.populate_filter_list(self.parent.uscite_table, 0, self.uscite_list)
        uscite_layout.addWidget(self.uscite_list)
        
        uscite_tab.setLayout(uscite_layout)
        tab_widget.addTab(uscite_tab, "Uscite")
        
        layout.addWidget(tab_widget)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Applica")
        apply_btn.clicked.connect(self.apply_filters)
        buttons_layout.addWidget(apply_btn)
        
        clear_btn = QPushButton("Rimuovi Filtri")
        clear_btn.clicked.connect(self.clear_filters)
        buttons_layout.addWidget(clear_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def populate_filter_list(self, table, column, list_widget):
        """Popola la lista con i valori unici dalla colonna"""
        values = set()
        for row in range(table.rowCount()):
            item = table.item(row, column)
            if item and item.text():
                values.add(item.text())
        
        for value in sorted(values):
            item = QListWidgetItem(value)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            list_widget.addItem(item)
    
    def apply_filters(self):
        """Applica i filtri selezionati"""
        # Filtri Entrate
        entrate_values = [
            self.entrate_list.item(i).text()
            for i in range(self.entrate_list.count())
            if self.entrate_list.item(i).checkState() == Qt.Checked
        ]
        self.parent.apply_filter(self.parent.entrate_table, 0, entrate_values)
        
        # Filtri Uscite
        uscite_values = [
            self.uscite_list.item(i).text()
            for i in range(self.uscite_list.count())
            if self.uscite_list.item(i).checkState() == Qt.Checked
        ]
        self.parent.apply_filter(self.parent.uscite_table, 0, uscite_values)
        
        self.accept()
    
    def clear_filters(self):
        """Rimuove tutti i filtri"""
        for table in [self.parent.entrate_table, self.parent.uscite_table]:
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)
        self.accept() 
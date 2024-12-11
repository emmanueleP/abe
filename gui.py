from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QAction, QDialog, QComboBox, QHBoxLayout,
    QSpinBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QUrl
from file_handler import handle_file
from settings import settings
import os
from io import BytesIO
from datetime import datetime
import json

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Tema
        theme_group = QGroupBox("Tema")
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(settings.get_theme())
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Anno e Reset
        year_group = QGroupBox("Gestione Anno e Protocollo")
        year_layout = QVBoxLayout()
        
        # Anno selector
        year_row = QHBoxLayout()
        year_label = QLabel("Anno:")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(int(settings.current_settings["year"]))
        year_row.addWidget(year_label)
        year_row.addWidget(self.year_spin)
        year_layout.addLayout(year_row)
        
        # Reset button e info
        reset_row = QHBoxLayout()
        reset_button = QPushButton("Azzera Numerazione")
        reset_button.clicked.connect(self.reset_protocol)
        reset_button.setStyleSheet("background-color: #2778ba;")
        
        # Numero corrente
        current_number = settings.current_settings["last_protocol_number"]
        self.protocol_info = QLabel(f"Ultimo numero: {current_number:05d}")
        
        reset_row.addWidget(self.protocol_info)
        reset_row.addWidget(reset_button)
        year_layout.addLayout(reset_row)
        
        year_group.setLayout(year_layout)
        layout.addWidget(year_group)

        # Timbro
        stamp_group = QGroupBox("Timbro")
        stamp_layout = QVBoxLayout()
        
        # Preview del timbro
        self.stamp_preview = QLabel("Nessun timbro caricato")
        self.stamp_preview.setAlignment(Qt.AlignCenter)
        self.stamp_preview.setMinimumHeight(150)
        stamp_layout.addWidget(self.stamp_preview)
        
        # Pulsante carica timbro
        stamp_button = QPushButton("Carica Timbro")
        stamp_button.clicked.connect(self.load_stamp)
        stamp_layout.addWidget(stamp_button)
        
        stamp_group.setLayout(stamp_layout)
        layout.addWidget(stamp_group)

        # Cartella Output
        output_group = QGroupBox("Cartella Output")
        output_layout = QHBoxLayout()
        
        self.output_path = QLabel(settings.current_settings["output_directory"])
        self.output_path.setWordWrap(True)
        output_layout.addWidget(self.output_path)
        
        change_path_btn = QPushButton("Cambia")
        change_path_btn.clicked.connect(self.change_output_path)
        output_layout.addWidget(change_path_btn)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Pulsante salva
        save_button = QPushButton("Salva")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.load_current_stamp()

    def load_stamp(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona Timbro",
            "",
            "Immagini (*.png *.jpg *.jpeg)"
        )
        if file_path:
            if settings.save_stamp_image(file_path):
                self.load_current_stamp()
            else:
                QMessageBox.critical(self, "Errore", "Impossibile caricare il timbro")

    def load_current_stamp(self):
        stamp = settings.get_stamp_image()
        if stamp:
            # Converti l'immagine PIL in QPixmap
            with BytesIO() as bio:
                stamp.save(bio, 'PNG')
                pixmap = QPixmap()
                pixmap.loadFromData(bio.getvalue())
                self.stamp_preview.setPixmap(pixmap.scaled(
                    150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
        else:
            self.stamp_preview.setText("Nessun timbro caricato")

    def save_settings(self):
        settings.set_theme(self.theme_combo.currentText())
        settings.set_year(self.year_spin.value())
        settings.ensure_output_directory()
        self.parent().apply_theme()
        self.accept()

    def reset_protocol(self):
        reply = QMessageBox.question(
            self,
            'Conferma Reset',
            f'Vuoi davvero azzerare la numerazione per l\'anno {self.year_spin.value()}?\n'
            'Questa operazione non può essere annullata.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            settings.reset_protocol_number(str(self.year_spin.value()))
            self.protocol_info.setText("Ultimo numero: 00000")
            QMessageBox.information(
                self,
                "Completato",
                f"Numerazione azzerata per l'anno {self.year_spin.value()}"
            )

    def change_output_path(self):
        """Cambia la cartella di output"""
        new_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Cartella Output",
            settings.current_settings["output_directory"],
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if new_path:
            try:
                # Verifica i permessi di scrittura
                test_file = os.path.join(new_path, "test.txt")
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                except:
                    raise Exception("Impossibile scrivere nella cartella selezionata")
                
                settings.set_output_directory(new_path)
                self.output_path.setText(new_path)
                
                QMessageBox.information(
                    self,
                    "Completato",
                    f"Cartella di output cambiata con successo.\n"
                    f"I nuovi documenti verranno salvati in:\n"
                    f"{settings.get_output_directory()}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Impossibile utilizzare la cartella selezionata:\n{str(e)}"
                )

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
        title = QLabel("Abe")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Versione
        version = QLabel("Versione 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        # Descrizione
        description = QLabel(
            "Questo software permette di protocollare automaticamente "
            "documenti in vari formati (PDF, DOCX, XLSX, immagini) "
            "aggiungendo un numero progressivo, data/ora e un eventuale timbro personalizzato."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignJustify)
        layout.addWidget(description)

        # Formati supportati
        formats = QLabel(
            "Formati supportati:\n"
            "• PDF (.pdf)\n"
            "• Word (.docx)\n"
            "• Excel (.xlsx)\n"
            "• Immagini (.png, .jpg, .jpeg)"
        )
        formats.setAlignment(Qt.AlignLeft)
        layout.addWidget(formats)

        # Copyright
        copyright = QLabel("© 2024 - Emmanuele Pani")
        copyright.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright)

        # Pulsante chiudi
        close_button = QPushButton("Chiudi")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

class ProtocolGUI(QMainWindow):
    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.setWindowTitle("Protocolla Documenti")
        self.setGeometry(200, 200, 800, 600)

        self.file_path = None
        
        # Disabilita il pulsante di protocollazione all'avvio
        self.protocol_button = None
        
        self.setup_menu()
        self.setup_ui()
        
        # Applica il tema solo se app è stato fornito
        if self.app:
            self.apply_theme()

    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        load_action = QAction('Carica Documento...', self)
        load_action.triggered.connect(self.load_document)
        load_action.setShortcut('Ctrl+O')
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Esci', self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(exit_action)
        
        # Menu Strumenti
        tools_menu = menubar.addMenu('Strumenti')
        
        history_action = QAction('Cronologia Anno...', self)
        history_action.triggered.connect(self.show_history)
        tools_menu.addAction(history_action)
        
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
        # Layout principale
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Gruppo Protocollo
        protocol_group = QGroupBox("Numerazione Protocollo")
        protocol_layout = QHBoxLayout()
        
        # Numero corrente
        current_number = settings.current_settings["last_protocol_number"] + 1
        protocol_label = QLabel(f"Prossimo numero: {current_number:05d}")
        protocol_layout.addWidget(protocol_label)
        
        protocol_group.setLayout(protocol_layout)
        main_layout.addWidget(protocol_group)

        # Preview
        self.preview_label = QLabel("Anteprima Documento")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        main_layout.addWidget(self.preview_label)

        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        self.upload_button = QPushButton("Carica Documento")
        self.upload_button.clicked.connect(self.load_document)
        buttons_layout.addWidget(self.upload_button)

        self.protocol_button = QPushButton("Protocolla")
        self.protocol_button.clicked.connect(self.protocol_document)
        self.protocol_button.setEnabled(False)
        buttons_layout.addWidget(self.protocol_button)
        
        main_layout.addLayout(buttons_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    def apply_theme(self):
        from qt_material import apply_stylesheet
        theme = f"{settings.get_theme()}_teal.xml"
        apply_stylesheet(self.app, theme=theme)

    def load_document(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Seleziona Documento", 
                "", 
                "Documenti (*.pdf *.docx *.xlsx *.png *.jpg *.jpeg)"
            )
            if file_path:
                self.file_path = file_path
                if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                    pixmap = QPixmap(file_path)
                    self.preview_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
                else:
                    filename = os.path.basename(file_path)
                    self.preview_label.setText(f"File caricato: {filename}")
                    
                # Abilita il pulsante di protocollazione
                self.protocol_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento del file: {str(e)}")

    def protocol_document(self):
        if not self.file_path:
            QMessageBox.warning(self, "Attenzione", "Carica un documento prima di protocollare.")
            return

        try:
            result = handle_file(self.file_path)
            QMessageBox.information(self, "Successo", result)
            self.preview_label.setText(result)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la protocollazione: {str(e)}")

    def show_history(self):
        dialog = HistoryDialog(self)
        dialog.exec_()

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cronologia Protocolli")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Selezione Anno
        year_layout = QHBoxLayout()
        year_label = QLabel("Anno:")
        self.year_combo = QComboBox()
        self.year_combo.addItems(self.get_available_years())
        self.year_combo.setCurrentText(str(datetime.now().year))
        self.year_combo.currentTextChanged.connect(self.load_history)
        
        # Pulsante elimina cronologia
        delete_btn = QPushButton("Elimina Cronologia")
        delete_btn.clicked.connect(self.delete_history)
        delete_btn.setStyleSheet("background-color: #ff4444; color: white;")
        
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_combo)
        year_layout.addStretch()
        year_layout.addWidget(delete_btn)
        layout.addLayout(year_layout)
        
        # Tabella cronologia
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Numero", "Data", "Ora", "Nome File", "Percorso"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        # Abilita la selezione doppio click
        self.table.doubleClicked.connect(self.open_selected_file)
        layout.addWidget(self.table)
        
        # Pulsanti azione
        buttons_layout = QHBoxLayout()
        
        open_file_btn = QPushButton("Apri File")
        open_file_btn.clicked.connect(self.open_selected_file)
        buttons_layout.addWidget(open_file_btn)
        
        open_folder_btn = QPushButton("Apri Cartella")
        open_folder_btn.clicked.connect(self.open_selected_folder)
        buttons_layout.addWidget(open_folder_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.load_history()

    def get_available_years(self):
        """Recupera gli anni disponibili dal file di log"""
        try:
            with open('protocol_history.json', 'r') as f:
                history = json.load(f)
                return sorted(history.keys(), reverse=True)
        except:
            return [str(datetime.now().year)]

    def load_history(self):
        """Carica la cronologia per l'anno selezionato"""
        try:
            self.table.clearContents()
            self.table.setRowCount(0)
            
            with open('protocol_history.json', 'r', encoding='utf-8') as f:
                history = json.load(f)
                year = self.year_combo.currentText()
                year_history = history.get(year, [])
                
                self.table.setRowCount(len(year_history))
                for i, entry in enumerate(year_history):
                    # Imposta gli item e rendi le celle non modificabili
                    items = [
                        QTableWidgetItem(entry['number']),
                        QTableWidgetItem(entry['date']),
                        QTableWidgetItem(entry['time']),
                        QTableWidgetItem(os.path.basename(entry['file'])),
                        QTableWidgetItem(entry['file'])
                    ]
                    
                    for col, item in enumerate(items):
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Rendi non modificabile
                        self.table.setItem(i, col, item)
                
                # Adatta le colonne al contenuto
                self.table.resizeColumnsToContents()
                # Mantieni l'allungamento per le colonne del nome file e percorso
                self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
                self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
                
                # Seleziona la prima riga se presente
                if self.table.rowCount() > 0:
                    self.table.selectRow(0)
                    
        except Exception as e:
            print(f"Errore nel caricamento della cronologia: {e}")
            self.table.setRowCount(0)

    def delete_history(self):
        """Elimina la cronologia per l'anno selezionato"""
        year = self.year_combo.currentText()
        reply = QMessageBox.question(
            self,
            'Conferma Eliminazione',
            f'Vuoi davvero eliminare la cronologia dell\'anno {year}?\n'
            'Questa operazione non può essere annullata.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with open('protocol_history.json', 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                if year in history:
                    del history[year]
                    
                    with open('protocol_history.json', 'w', encoding='utf-8') as f:
                        json.dump(history, f, indent=4, ensure_ascii=False)
                    
                    # Aggiorna la combo degli anni
                    self.year_combo.clear()
                    self.year_combo.addItems(self.get_available_years())
                    
                    # Se non ci sono più anni, aggiungi l'anno corrente
                    if self.year_combo.count() == 0:
                        current_year = str(datetime.now().year)
                        self.year_combo.addItem(current_year)
                    
                    self.year_combo.setCurrentText(str(datetime.now().year))
                    self.load_history()
                    
                    QMessageBox.information(
                        self,
                        "Completato",
                        f"Cronologia dell'anno {year} eliminata con successo"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Errore",
                    f"Errore durante l'eliminazione della cronologia: {str(e)}"
                )

    def open_selected_file(self):
        """Apre il file selezionato"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            file_path = self.table.item(current_row, 4).text()
            if os.path.exists(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            else:
                QMessageBox.warning(
                    self,
                    "File non trovato",
                    f"Il file non esiste più nel percorso:\n{file_path}"
                )

    def open_selected_folder(self):
        """Apre la cartella contenente il file selezionato"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            file_path = self.table.item(current_row, 4).text()
            folder_path = os.path.dirname(file_path)
            if os.path.exists(folder_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            else:
                QMessageBox.warning(
                    self,
                    "Cartella non trovata",
                    f"La cartella non esiste più nel percorso:\n{folder_path}"
                )

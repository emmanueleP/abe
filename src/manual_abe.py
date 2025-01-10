from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QLabel, QScrollArea, QWidget
from PyQt5.QtCore import Qt

class ManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manuale Utente")
        self.setFixedSize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        
        # Tab Introduzione
        intro_tab = self.create_scrollable_tab("""
            <h2>Benvenuto in Abe-Gestionale</h2>
            <p>Questa suite di applicazioni è stata sviluppata per semplificare 
            la gestione della segreteria di una sede Avis.</p>
            <p>Seleziona una sezione per visualizzare le istruzioni specifiche.</p>
        """)
        tab_widget.addTab(intro_tab, "Introduzione")
        
        # Tab Ordina
        ordina_tab = self.create_scrollable_tab("""
            <h2>📝 Ordina - Protocollazione Documenti</h2>
            <h3>Funzionalità principali:</h3>
            <ul>
                <li>Protocollazione automatica di documenti</li>
                <li>Supporto per PDF, Word, Excel e immagini</li>
                <li>Timbro digitale personalizzato</li>
                <li>Archivio cronologico per anno</li>
            </ul>
            <h3>Come usare:</h3>
            <ol>
                <li>Clicca su "Seleziona File" o trascina i file</li>
                <li>Il documento verrà automaticamente protocollato</li>
                <li>I file vengono salvati in Documents/Abe/Ordina/anno</li>
            </ol>
        """)
        tab_widget.addTab(ordina_tab, "Ordina")
        
        # Tab aViS66
        avis_tab = self.create_scrollable_tab("""
            <h2>👥 aViS66 - Gestione Libro Soci</h2>
            <h3>Funzionalità principali:</h3>
            <ul>
                <li>Gestione completa anagrafica donatori</li>
                <li>Compatibilità con il SIAN</li>
                <li>Importazione/esportazione dati</li>
            </ul>
            <h3>Come usare:</h3>
            <ol>
                <li>Usa il menu File per gestire i dati</li>
                <li>Doppio click su una riga per modificare</li>
                <li>Usa i filtri per cercare donatori</li>
            </ol>
        """)
        tab_widget.addTab(avis_tab, "aViS66")
        
        # Tab PDFtoA
        pdftoa_tab = self.create_scrollable_tab("""
            <h2>📄 PDFtoA - Conversione PDF/A</h2>
            <h3>Funzionalità principali:</h3>
            <ul>
                <li>Conversione in formato PDF/A</li>
                <li>Validazione conformità</li>
                <li>Conversione batch</li>
            </ul>
            <h3>Come usare:</h3>
            <ol>
                <li>Seleziona i file da convertire</li>
                <li>Scegli le opzioni di conversione</li>
                <li>Avvia la conversione</li>
            </ol>
        """)
        tab_widget.addTab(pdftoa_tab, "PDFtoA")
        
        # Tab ManRev
        manrev_tab = self.create_scrollable_tab("""
            <h2>💰 ManRev - Mandati e Reversali</h2>
            <h3>Funzionalità principali:</h3>
            <ul>
                <li>Generazione automatica documenti</li>
                <li>Numerazione progressiva</li>
                <li>Gestione firme digitali</li>
            </ul>
            <h3>Come usare:</h3>
            <ol>
                <li>Seleziona il tipo di documento</li>
                <li>Compila i campi richiesti</li>
                <li>Genera e stampa il documento</li>
            </ol>
        """)
        tab_widget.addTab(manrev_tab, "ManRev")
        
        # Tab Agenda
        agenda_tab = self.create_scrollable_tab("""
            <h2>📅 Agenda - Gestione Eventi</h2>
            <h3>Funzionalità principali:</h3>
            <ul>
                <li>Calendario interattivo</li>
                <li>Notifiche personalizzate</li>
                <li>Categorie eventi</li>
            </ul>
            <h3>Come usare:</h3>
            <ol>
                <li>Clicca su un giorno per vedere/aggiungere eventi</li>
                <li>Configura le notifiche nelle impostazioni</li>
                <li>Usa le categorie per organizzare gli eventi</li>
            </ol>
        """)
        tab_widget.addTab(agenda_tab, "Agenda")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
    
    def create_scrollable_tab(self, content):
        """Crea una tab scrollabile con contenuto HTML"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        label = QLabel()
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setText(content)
        label.setOpenExternalLinks(True)
        
        content_layout.addWidget(label)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        return scroll 
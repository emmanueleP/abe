import sqlite3
import os
from datetime import datetime

class ProtocolDatabase:
    def __init__(self):
        # Crea la directory base se non esiste
        self.base_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "Abe",
            "Ordina",
            str(datetime.now().year)
        )
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Percorso del database
        self.db_path = os.path.join(self.base_dir, "protocol_history.db")
        
        # Inizializza il database
        self.init_db()
    
    def init_db(self):
        """Inizializza il database se non esiste"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Crea la tabella se non esiste
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS protocol_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_number TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crea l'indice sul numero di protocollo
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_protocol ON protocol_history(protocol_number)')
            
            # Verifica se la colonna year esiste
            cursor.execute('PRAGMA table_info(protocol_history)')
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'year' not in columns:
                # Aggiungi la colonna year
                cursor.execute('ALTER TABLE protocol_history ADD COLUMN year INTEGER')
                # Aggiorna i valori dell'anno per i record esistenti
                cursor.execute('''
                    UPDATE protocol_history 
                    SET year = CAST(strftime('%Y', timestamp) AS INTEGER)
                    WHERE year IS NULL
                ''')
                # Crea l'indice sull'anno
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON protocol_history(year)')
            
            conn.commit()
    
    def add_entry(self, protocol_number, file_path):
        """Aggiunge una nuova voce al database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute(
                'INSERT INTO protocol_history (protocol_number, file_path, year) VALUES (?, ?, ?)',
                (protocol_number, file_path, now.year)
            )
            conn.commit()
    
    def get_history(self, limit=100):
        """Recupera la cronologia dei protocolli"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM protocol_history ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            return cursor.fetchall()
    
    def search_protocol(self, protocol_number):
        """Cerca un protocollo specifico"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM protocol_history WHERE protocol_number LIKE ?',
                (f'%{protocol_number}%',)
            )
            return cursor.fetchall()
    
    def get_available_years(self):
        """Restituisce la lista degli anni disponibili nel database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT year FROM protocol_history WHERE year IS NOT NULL ORDER BY year DESC')
                years = cursor.fetchall()
                return [str(year[0]) for year in years] if years else [str(datetime.now().year)]
        except sqlite3.OperationalError:
            # Se qualcosa va storto, restituisci almeno l'anno corrente
            return [str(datetime.now().year)] 
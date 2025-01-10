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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS protocol_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_number TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_protocol ON protocol_history(protocol_number)')
            conn.commit()
    
    def add_entry(self, protocol_number, file_path):
        """Aggiunge una nuova voce al database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO protocol_history (protocol_number, file_path) VALUES (?, ?)',
                (protocol_number, file_path)
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
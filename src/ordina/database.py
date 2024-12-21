import sqlite3
import os
from datetime import datetime
from .settings import ordina_settings as settings

class ProtocolDatabase:
    def __init__(self):
        self.year = str(datetime.now().year)
        self.update_db_path()

    def update_db_path(self):
        """Aggiorna il percorso del database in base all'anno"""
        # Usa la directory dei protocolli dell'anno
        self.db_dir = os.path.join(settings.get_output_directory())
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, f'cronologia_{self.year}.db')
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS protocol_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_number TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    year TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add_entry(self, protocol_number, file_path):
        now = datetime.now()
        current_year = str(now.year)
        
        # Se l'anno è cambiato, aggiorna il percorso del database
        if current_year != self.year:
            self.year = current_year
            self.update_db_path()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO protocol_history 
                (protocol_number, date, time, file_path, year)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                protocol_number,
                now.strftime('%d/%m/%Y'),
                now.strftime('%H:%M:%S'),
                file_path,
                self.year
            ))
            conn.commit()

    def get_entries_by_year(self, year):
        """Recupera le voci per un anno specifico"""
        # Aggiorna il percorso del database per l'anno richiesto
        if year != self.year:
            self.year = year
            self.update_db_path()
        
        if not os.path.exists(self.db_path):
            return []
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT protocol_number, date, time, file_path
                FROM protocol_history
                WHERE year = ?
                ORDER BY id DESC
            ''', (year,))
            return cursor.fetchall()

    def search_entries(self, search_text):
        """Cerca nelle voci del protocollo"""
        results = []
        # Cerca in tutti gli anni disponibili
        for year in self.get_available_years():
            if year != self.year:
                self.year = year
                self.update_db_path()
            
            if os.path.exists(self.db_path):
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    search_pattern = f"%{search_text}%"
                    cursor.execute('''
                        SELECT protocol_number, date, time, file_path, year
                        FROM protocol_history
                        WHERE protocol_number LIKE ? OR file_path LIKE ?
                        ORDER BY id DESC
                    ''', (search_pattern, search_pattern))
                    results.extend(cursor.fetchall())
        
        return results

    def get_available_years(self):
        """Recupera gli anni disponibili cercando i database nelle cartelle"""
        years = []
        base_dir = os.path.dirname(settings.get_output_directory())
        
        try:
            # Cerca in tutte le cartelle degli anni
            for year_dir in os.listdir(base_dir):
                if os.path.isdir(os.path.join(base_dir, year_dir)):  # Verifica che sia una directory
                    db_path = os.path.join(base_dir, year_dir, f'cronologia_{year_dir}.db')
                    if os.path.exists(db_path):
                        years.append(year_dir)
        except Exception as e:
            print(f"Errore nel recupero degli anni: {e}")
            years = [str(datetime.now().year)]  # Fallback all'anno corrente
        
        return sorted(years, reverse=True) if years else [str(datetime.now().year)]

    def delete_year(self, year):
        """Elimina il database di un anno specifico"""
        db_path = os.path.join(
            settings.get_output_directory().replace(self.year, year),
            f'cronologia_{year}.db'
        )
        if os.path.exists(db_path):
            os.remove(db_path) 
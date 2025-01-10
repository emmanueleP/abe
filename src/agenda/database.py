import sqlite3
import os
from datetime import datetime

class AgendaDB:
    def __init__(self, year=None, month=None):
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
            
        self.year = year
        self.month = month
        self.db_dir = os.path.join(os.path.expanduser("~"), "Documents", "Abe", "Agenda", str(year))
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, f"{month:02d}_{year}.db")
        self.init_db()
    
    def init_db(self):
        """Inizializza il database se non esiste"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    time TEXT,
                    category TEXT,
                    priority INTEGER DEFAULT 0,
                    notify BOOLEAN DEFAULT 0,
                    notify_minutes INTEGER DEFAULT 15,
                    completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_day ON events(day)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON events(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON events(priority)')
            conn.commit()
    
    def add_event(self, day, title, description="", time="", category="", priority=0):
        """Aggiunge un nuovo evento"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (day, title, description, time, category, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (day, title, description, time, category, priority))
            conn.commit()
            return cursor.lastrowid
    
    def get_events(self, day=None, category=None):
        """Recupera eventi con filtri opzionali"""
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if day is not None:
            query += " AND day = ?"
            params.append(day)
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " ORDER BY time, priority DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def update_event(self, event_id, **kwargs):
        """Aggiorna un evento esistente"""
        valid_fields = {'title', 'description', 'time', 'category', 'priority', 'completed'}
        updates = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not updates:
            return False
            
        query = "UPDATE events SET " + ", ".join(f"{k}=?" for k in updates)
        query += ", updated_at=CURRENT_TIMESTAMP WHERE id=?"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(updates.values()) + [event_id])
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_event(self, event_id):
        """Elimina un evento"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id=?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0 
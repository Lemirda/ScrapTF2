import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlite3
from config import get_application_path


class RaffleDatabase:

    def __init__(self, db_file=None):
        if db_file is None:
            db_file = os.path.join(get_application_path(), "raffles.db")
        self.db_file = db_file
        self.conn = None
        self.create_tables()

    DEFAULT_SETTINGS = {
        'language': '',
        'logged_in': '0',
        'scan_delay_min': '5',
        'scan_delay_max': '10',
        'wait_minutes_min': '5',
        'wait_minutes_max': '20',
    }

    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raffles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            processed INTEGER DEFAULT 0
        )
        ''')

        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_raffles_url ON raffles(url)')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')

        cursor.execute('SELECT COUNT(*) FROM settings')
        if cursor.fetchone()[0] == 0:
            for key, value in self.DEFAULT_SETTINGS.items():
                cursor.execute(
                    'INSERT INTO settings (key, value) VALUES (?, ?)',
                    (key, value))

        conn.commit()

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file, timeout=30)
            self.conn.execute('PRAGMA journal_mode=WAL')
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def add_raffle(self, url):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO raffles (url, processed) VALUES (?, 0)',
            (url,)
        )
        conn.commit()
        rows_affected = cursor.rowcount
        return rows_affected > 0

    def delete_raffle(self, url):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM raffles WHERE url = ?', (url,))
        conn.commit()
        return cursor.rowcount > 0

    def is_raffle_exists(self, url):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT 1 FROM raffles WHERE url = ?', (url,))
        return cursor.fetchone() is not None

    def mark_as_processed(self, url):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            'UPDATE raffles SET processed = 1 WHERE url = ?',
            (url,)
        )
        conn.commit()
        return cursor.rowcount > 0

    def get_unprocessed_raffles(self, limit=None):
        conn = self.connect()
        cursor = conn.cursor()

        if limit is not None:
            cursor.execute(
                'SELECT * FROM raffles WHERE processed = 0 LIMIT ?',
                (limit,)
            )
        else:
            cursor.execute('SELECT * FROM raffles WHERE processed = 0')

        return cursor.fetchall()

    def get_stats(self):
        conn = self.connect()
        cursor = conn.cursor()

        stats = {}

        cursor.execute('SELECT COUNT(*) FROM raffles')
        stats['total'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM raffles WHERE processed = 0')
        stats['unprocessed'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM raffles WHERE processed = 1')
        stats['processed'] = cursor.fetchone()[0]

        return stats

    def get_setting(self, key):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def set_setting(self, key, value):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, str(value)))
        conn.commit()

    def get_all_settings(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        return {row[0]: row[1] for row in cursor.fetchall()}

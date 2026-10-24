import sqlite3
import os

class MemoryManager:
    def __init__(self, db_path="memory/jarvis_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_message(self, role, content):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO conversation_history (role, content) VALUES (?, ?)", (role, content))
            conn.commit()

    def get_recent_history(self, limit=10):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?", 
                (limit,)
            )
            rows = cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def remember(self, key, value):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO long_term_memory (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
                (key, value)
            )
            conn.commit()

    def recall(self, key):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM long_term_memory WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def dump_knowledge(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM long_term_memory")
            return {k: v for k, v in cursor.fetchall()}
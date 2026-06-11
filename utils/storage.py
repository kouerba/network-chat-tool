import sqlite3
from pathlib import Path
from datetime import datetime
from core.config import Config

class Storage:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_db()
    
    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id TEXT PRIMARY KEY,
                        msg_type TEXT,
                        from_user TEXT,
                        from_id TEXT,
                        to_user TEXT,
                        to_id TEXT,
                        content TEXT,
                        timestamp TEXT,
                        read INTEGER DEFAULT 0
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT,
                        ip TEXT,
                        tcp_port INTEGER,
                        last_seen TEXT
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Failed to init database: {e}")
    
    def save_message(self, message_id: str, msg_type: str, from_user: str,
                    from_id: str, to_user: str, to_id: str, content: str,
                    timestamp: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO messages
                    (id, msg_type, from_user, from_id, to_user, to_id, content, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (message_id, msg_type, from_user, from_id, to_user, to_id, content, timestamp))
                conn.commit()
        except Exception as e:
            print(f"Failed to save message: {e}")
    
    def get_messages(self, limit: int = 100) -> list:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?',
                    (limit,)
                )
                return cursor.fetchall()
        except Exception as e:
            print(f"Failed to get messages: {e}")
            return []
    
    def get_chat_history(self, user_id: str, limit: int = 100) -> list:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM messages
                    WHERE (from_id = ? OR to_id = ?)
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, user_id, limit))
                return cursor.fetchall()
        except Exception as e:
            print(f"Failed to get chat history: {e}")
            return []

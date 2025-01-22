import sqlite3
from typing import List, Tuple
from datetime import datetime

class DataBaseOps:
    def __init__(self):
        self.db = sqlite3.connect('learning_bot.db')
        self.setup_db()

    def setup_db(self):
        cursor = self.db.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
                       user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT,
                       level TEXT,
                       join_time DATETIME)        
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
                       q_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       question TEXT,
                       q_level TEXT)
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pros (
                       pro_id INTEGER PRIMARY KEY,
                       name TEXT,
                       num_evals INTEGER)
        ''')

        self.db.commit()

    def insert_q(self, questions: List[Tuple[str, str]]):
        cursor = self.db.cursor()

        for q, level in questions:
            cursor.execute('''
            INSERT INTO questions (question, q_level) VALUES (?, ?)
            ''', (q, level))
        
        self.db.commit()

    def insert_user(self, name='no_name', level='beginner'):
        cursor = self.db.cursor()

        cursor.execute('''
        INSERT INTO users (name, level, join_time) VALUES (?, ?, ?)
        ''', (name, level, datetime.now()))

        self.db.commit()



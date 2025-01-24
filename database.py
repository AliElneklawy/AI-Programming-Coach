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
                       user_id INTEGER PRIMARY KEY,
                       score INTEGER,
                       name TEXT,
                       level TEXT,
                       join_time DATETIME,
                       is_expert BOOLEAN DEFAULT FALSE)        
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
                       q_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       question TEXT,
                       q_level TEXT)
        ''')

        # cursor.execute('''
        # CREATE TABLE IF NOT EXISTS pros (
        #                pro_id INTEGER PRIMARY KEY,
        #                name TEXT,
        #                num_evals INTEGER)
        # ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assesments (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                user_answer TEXT,
                is_correct BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        self.db.commit()

    def insert_q(self, questions: List[Tuple[str, str]]):
        cursor = self.db.cursor()

        for q, level in questions:
            cursor.execute('''
            INSERT INTO questions (question, q_level) VALUES (?, ?)
            ''', (q, level))
        
        self.db.commit()

    def insert_user(self, user_id, score, name='no_name', level='beginner'):
        cursor = self.db.cursor()

        is_expert = level.lower() == 'advanced'
        cursor.execute('''
        INSERT INTO users (user_id, score, name, level, join_time, is_expert)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, score, name, level, datetime.now(), is_expert))

        self.db.commit()

    def insert_assesment(self, user_id, q, ans, is_correct, time):
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO assesments (user_id, question, user_answer, is_correct, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, q, ans, is_correct, time))

        self.db.commit()

    def get_questions(self, q_level: str):
        cursor = self.db.cursor()
        cursor.execute('''
        SELECT question FROM questions WHERE q_level == ?
        ''', (q_level,))
        questions = cursor.fetchall()

        return questions
    
    def get_users(self, id=None):
        cursor = self.db.cursor()

        if not id:
            cursor.execute('''
            SELECT * FROM users
            ''')
            users = cursor.fetchall()
            return users
        
        cursor.execute('''
        SELECT user_id FROM users WHERE user_id == ?
        ''', (id,))

        user = cursor.fetchone()
        return user
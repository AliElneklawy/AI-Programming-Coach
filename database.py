import sqlite3
from typing import List, Tuple
from datetime import datetime

class DataBaseOps:
    def __init__(self) -> None:
        self.db = sqlite3.connect('learning_bot.db')
        self.setup_db()

    def setup_db(self) -> None:
        cursor = self.db.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
                       user_id INTEGER PRIMARY KEY,
                       score INTEGER,
                       name TEXT,
                       level TEXT,
                       current_question TEXT,
                       join_time DATETIME,
                       last_assessment DATETIME,
                       task_interval INT,
                       is_expert BOOLEAN DEFAULT FALSE)        
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
                       q_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       question TEXT UNIQUE,
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


    def insert_q(self, questions: List[Tuple[str, str]]) -> None:
        cursor = self.db.cursor()

        # for q, level in questions:
        #     try:
        #         cursor.execute('''
        #         INSERT INTO questions (question, q_level) VALUES (?, ?)
        #         ''', (q, level))
        #     except sqlite3.IntegrityError:
        #         print(f"Skipping existing questions: {q}")

        with self.db:
            for q, level in questions:
                cursor.execute('''
                INSERT OR IGNORE INTO questions (question, q_level) 
                VALUES (?, ?)
                ''', (q, level))

        # for q, level in questions:
        #     cursor.execute('''
        #     INSERT INTO questions (question, q_level) 
        #     VALUES (?, ?)
        #     ON CONFLICT(question) DO UPDATE
        #     SET q_level = excluded.q_level
        #     RETURNING question;
        #     ''', (q, level))
        
        # self.db.commit()


    def insert_user(self, user_id: int, 
                    score: int, name='no_name', 
                    level='beginner',
                    task_interval=24, 
                    last_assessment=datetime.now()) -> None:
        cursor = self.db.cursor()

        is_expert = level.lower() == 'advanced'
        cursor.execute('''
        INSERT INTO users (user_id, score, name, level, join_time, last_assessment, task_interval, is_expert)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, score, name, level, datetime.now(), last_assessment, task_interval, is_expert))

        self.db.commit()


    def insert_assesment(self, user_id: int, q: str, ans: str, is_correct, time) -> None:
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO assesments (user_id, question, user_answer, is_correct, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, q, ans, is_correct, time))

        self.db.commit()


    def delete_user(self, user_id):
        cursor = self.db.cursor()
        cursor.execute('''
        DELETE FROM users WHERE user_id = ?
        ''', (user_id,))

        self.db.commit()

    
    def delete_q(self, q_id):
        cursor = self.db.cursor()
        cursor.execute('''
        DELETE FROM questions
        WHERE q_id = ?
        ''', (q_id,))

        self.db.commit()


    def get_questions(self, q_level: str = None) -> List[Tuple]:
        cursor = self.db.cursor()

        if q_level: # query based on question level
            cursor.execute('''
            SELECT question FROM questions WHERE q_level == ?
            ''', (q_level,))
        else:
            cursor.execute('''
            SELECT * FROM questions
            ''')
            
        questions = cursor.fetchall()
        return questions
        
    
    def get_users(self, id=None, daily_task=False):
        cursor = self.db.cursor()

        if id: # selection based on id
            cursor.execute('''
            SELECT user_id, score, level 
            FROM users 
            WHERE user_id == ?
            ''', (id,))

            user = cursor.fetchone()
            return user
        
        if daily_task:
            cursor.execute('''
            SELECT user_id, level, last_assessment, task_interval
            FROM users
            ''')

            users = cursor.fetchall()
            return users
        
        cursor.execute('''
        SELECT * FROM users
        ''')
        users = cursor.fetchall()
        return users
    

    def update_user(self, new_score, user_id, assessment_time):
        cursor = self.db.cursor()

        cursor.execute('''
        UPDATE users
        SET score = ?,
            current_question = NULL,
            last_assessment = ?
        WHERE user_id = ?
        ''', (new_score, user_id, assessment_time))


    def execute_query(self, query: str, params: tuple = None):
        cursor = self.db.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        return cursor.fetchall()


    def get_top_learners(self, limit=10):
        """
        Retrieve top learners sorted by score in descending order
        :param limit: Maximum number of learners to return (default 10)
        :return: List of tuples (name, level, score)
        """
        cursor = self.db.cursor()

        cursor.execute('''
        SELECT name, level, score 
        FROM users 
        ORDER BY score DESC 
        LIMIT ?
        ''', (limit,))

        return cursor.fetchall()
    

    def update_interval(self, user_id: int, interval: int):
        cursor = self.db.cursor()

        cursor.execute('''
        UPDATE users 
        SET task_interval = ?
        WHERE user_id = ?
        ''', (interval, user_id))

        self.db.commit()
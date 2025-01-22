import os
from dotenv import load_dotenv

from teacher_bot import PythonLearningBot
from database import DataBaseOps
from constants import beginner_questions, initial_asses_qs


load_dotenv()

if __name__ == '__main__':
    COHERE_API = os.getenv('COHERE_API')
    
    db = DataBaseOps()
    bot = PythonLearningBot(COHERE_API)

    db.insert_q(beginner_questions)

    user_level = bot.initial_assesment(initial_asses_qs)
    db.insert_user(level=user_level)


import os
from dotenv import load_dotenv

from teacher_bot import PythonLearningBot
from database import DataBaseOps
from constants import (
                    beginner_questions, 
                    intermediate_questions, 
                    advanced_questions, 
                    initial_asses_qs,
                    )


load_dotenv()

if __name__ == '__main__':
    COHERE_API = os.getenv('COHERE_API')
    user_id = 1

    db = DataBaseOps()
    bot = PythonLearningBot(COHERE_API)

    db.insert_q(beginner_questions)
    db.insert_q(intermediate_questions)
    db.insert_q(advanced_questions)

    user_level = bot.initial_assesment(initial_asses_qs, user_id)
    db.insert_user(level=user_level)


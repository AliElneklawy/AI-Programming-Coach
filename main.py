from tg_bot import TelegramBot
from database import DataBaseOps
from constants import (
                    beginner_questions, 
                    intermediate_questions, 
                    advanced_questions, 
                    )


if __name__ == '__main__':
    bot = TelegramBot()
    db = DataBaseOps()

    db.insert_q(beginner_questions)
    db.insert_q(intermediate_questions)
    db.insert_q(advanced_questions)

    bot.run()

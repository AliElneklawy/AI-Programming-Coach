from database import DataBaseOps
from teacher_bot import PythonLearningBot
from constants import initial_asses_qs
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
from telegram.error import BadRequest
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    filters,
    CommandHandler,
    Application,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

START, QUESTION, END_ASSESSMENT = range(3)


class TelegramBot:
    def __init__(self):
        self.admins = [5859780703]
        self.db = DataBaseOps()
        self.teacher = PythonLearningBot()
        self.application = Application.builder().token(os.getenv('BOT_TOKEN')).build()
        
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start_command)],
            states={
                START: [
                    CallbackQueryHandler(self.button_handler)
                ],
                QUESTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_answer)
                ],
                END_ASSESSMENT: [
                    CommandHandler("start", self.start_command),
                    CallbackQueryHandler(self.button_handler)
                ]
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel_assessment),
                CommandHandler("start", self.start_command)
            ],
        )
        
        self.application.add_handler(self.conv_handler)
        # self.application.add_handler(CommandHandler("insert_q", self.insert_q))
        # self.application.add_handler(CommandHandler("ask_cohere", self.ask_cohere))
        # self.application.add_handler(CommandHandler("my_level", self.my_level))
        self.application.add_handlers(handlers={
            1: [CommandHandler("get_questions", self.get_questions),
                CommandHandler("insert_q", self.insert_q), 
                CommandHandler("ask_cohere", self.ask_cohere),
                CommandHandler("my_level", self.my_level),
                CommandHandler("unsubscribe", self.unsubscribe)]
        })


    def create_keyboard(self, texts: list, callbacks: list):
        keyboard = [
            [
                InlineKeyboardButton(texts[0], callback_data=callbacks[0]),
                InlineKeyboardButton(texts[1], callback_data=callbacks[1])
            ]
        ]

        return InlineKeyboardMarkup(keyboard)


    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['current_question_index'] = 0
        context.user_data['score'] = 0
        # context.user_data['level'] = 'beginner'
        
        first_name = update.effective_user.first_name
        user_id = update.effective_user.id
        
        user: tuple = self.db.get_users(user_id) # returns none if not exists
        if not user: # user not in the db
            msg = f"""
            Hello, {first_name}. I see this is the first time you use the bot. 
            How about you take an assessment to determine your level? Our assessment has {len(initial_asses_qs)} questions.
            """
            reply_markup = self.create_keyboard(texts=["Yes, let's start!", "No, maybe later"],
                                                callbacks=["start_assessment", "decline_assessment"])
            await update.message.reply_text(text=msg, reply_markup=reply_markup)
            return START
    
        msg = f"Welcome back, {first_name}."
        await update.message.reply_text(text=msg)
        return END_ASSESSMENT


    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        #logging.info(f"Button handler called with data: {query.data}")
        
        if query.data == 'stay':
            logging.info("Stay button pressed")
            await query.edit_message_text(text="We are glad to have you!")
            return END_ASSESSMENT
        
        elif query.data == 'unsubscribe':
            user_id = update.effective_user.id
            self.db.delete_user(user_id)
            await query.edit_message_text(text="You have been unsubscribed.")
            return ConversationHandler.END

        elif query.data == 'start_assessment':
            await query.edit_message_text(text="Great! Let's begin the assessment.")
            first_question, _ = initial_asses_qs[0]
            await query.message.reply_text(first_question)
            context.user_data['current_question_index'] = 0
            context.user_data['score'] = 0
            return QUESTION
        
        elif query.data == 'decline_assessment':
            await query.edit_message_text(text="Ok, you can start the assessment anytime.")
            return END_ASSESSMENT
        
        return END_ASSESSMENT


    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name
        user_answer = update.message.text

        current_index = context.user_data.get('current_question_index', 0)
        current_score = context.user_data.get('score', 0)

        if current_index >= len(initial_asses_qs):
            await update.message.reply_text("Assessment completed!")
            return END_ASSESSMENT

        question, weight = initial_asses_qs[current_index]
        
        message = f"Question: {question}. User Answer: {user_answer}"
        status = self.teacher.get_response(message)

        if status == 1:
            await update.message.reply_text("Correct!")
            current_score += weight
        else:
            await update.message.reply_text("Wrong.")

        self.db.insert_assesment(user_id, question, user_answer, status, datetime.now())

        current_index += 1
        
        context.user_data['current_question_index'] = current_index
        context.user_data['score'] = current_score

        if current_index < len(initial_asses_qs):
            next_question, _ = initial_asses_qs[current_index]
            await update.message.reply_text(next_question)
            return QUESTION
        else:
            if current_score <= 4:
                level = 'beginner'
            elif current_score <= 12:
                level = 'intermediate'
            else:
                level = 'advanced'

            self.db.insert_user(user_id, current_score, first_name, level)

            await update.message.reply_text(f"Assessment completed! Your level is: {level}")
            return END_ASSESSMENT


    async def cancel_assessment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the assessment."""
        await update.message.reply_text("Assessment cancelled.")
        return END_ASSESSMENT
        

    async def insert_q(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.admins:
            await update.message.reply_text("Sorry, this command is only available for admins.")
            return
        
        full_text = update.message.text
        args_text = full_text[len('/insert_q '):]
        *question_parts, level = args_text.rsplit(' ', 1)
        question = ' '.join(question_parts)
        q_qlevel = [(question, level.lower())]

        self.db.insert_q(q_qlevel)
        await update.message.reply_text(f"Question added: '{question}' with level: {level}")


    async def ask_cohere(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        question = ' '.join(args)
        msg = await update.message.reply_text('Thinking....')
        answer: str = self.teacher.get_response(question, 1)
        
        await msg.edit_text(answer)


    async def my_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        score_level = self.db.get_users(id=user_id) # returns (user_id, score, level)
        if score_level is None:
            await update.message.reply_text(f"Your are not subscribed to the bot.")
            return
        
        score, level = score_level[1], score_level[2]
        await update.message.reply_text(f"Your level is {level} with a score of {score}.")


    async def get_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id in self.admins:
            questions = self.db.get_questions()        
            message = "\n".join([f"{q[0]}. {q[1]} ({q[2]})" for q in questions])

            try:
                await update.message.reply_text(message)
            except BadRequest: # the message is empty
                await update.message.reply_text("No questions available.")
        else:
            await update.message.reply_text("Sorry, this command is only available for admins.")


    async def unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = "Are you sure you want to unsubscribe from the bot? ***All your records will be deleted***."
        reply_markup = self.create_keyboard(texts=["Yes, I'm sure", "No, I will stay"],
                                            callbacks=["unsubscribe", "stay"])
        await update.message.reply_text(text=msg, reply_markup=reply_markup, parse_mode='Markdown')


    async def send_daily_task(self):
        pass

    def run(self):
        print('======== Bot is running ========')
        self.application.run_polling()

bot = TelegramBot()
bot.run()

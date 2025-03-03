from database import DataBaseOps
from teacher_bot import PythonLearningBot
from constants import initial_asses_qs
from constants import score_weights
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
import os
import random
import logging
from enum import Enum, auto
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
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

# START, QUESTION, END_ASSESSMENT, DAILY_TASK  = range(4)

class ConvState(Enum):
    START = auto()
    QUESTION = auto()
    END_ASSESSMENT = auto()
    DAILY_TASK = auto()


class TelegramBot:
    def __init__(self):
        self.admins = [5859780703]
        self.db = DataBaseOps()
        self.teacher = PythonLearningBot()
        self.application = Application.builder().token(os.getenv('BOT_TOKEN')).build()
        
        self._setup_handlers()
        self._setup_jobs()


    def _setup_handlers(self):
        """Configure conversation and command handlers."""
        # Main conversation handler for assessment
        self.assessment_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start_command)],
            states={
                ConvState.START: [
                    CallbackQueryHandler(self.button_handler)
                ],
                ConvState.QUESTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_answer)
                ],
                ConvState.END_ASSESSMENT: [
                    CommandHandler("start", self.start_command),
                    CallbackQueryHandler(self.button_handler)
                ]
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel_assessment),
                CommandHandler("start", self.start_command)
            ],
            name="assessment_conversation"
        )
        
        self.application.add_handler(self.assessment_handler)
        
        # Add general message handler for daily tasks with low priority
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_daily_answer
            ),
            group=1  # Lower priority than conversation handler
        )
        
        self.application.add_handlers(handlers={
            2: [  # Even lower priority
                CommandHandler("get_questions", self.get_questions),
                CommandHandler("insert_q", self.insert_q),
                CommandHandler("delete_q", self.delete_q),
                CommandHandler("ask_cohere", self.ask_cohere),
                CommandHandler("my_level", self.my_level),
                CommandHandler("unsubscribe", self.unsubscribe),
                CommandHandler("skip", self.skip_daily_task),
                CommandHandler("top_learners", self.top_learners),
                CommandHandler("task_interval", self.task_interval)
            ]
        })


    def _setup_jobs(self):
        self.job_queue = self.application.job_queue
        self.job_queue.run_repeating(
            callback=self.send_daily_task,
            interval=timedelta(minutes=1)
        )
    

    @staticmethod
    def create_keyboard(texts: list, callbacks: list):
        """Creates an inline keyboard with two buttons.

        Args:
            texts (list): A list containing two button labels.
            callbacks (list): A list containing two callback data values corresponding to the buttons.

        Returns:
            InlineKeyboardMarkup: An inline keyboard with two buttons.
        """
        keyboard = [
            [
                InlineKeyboardButton(texts[0], callback_data=callbacks[0]),
                InlineKeyboardButton(texts[1], callback_data=callbacks[1])
            ]
        ]

        return InlineKeyboardMarkup(keyboard)


    @staticmethod
    def level_by_score(score: int):
        """Determines the user's skill level based on their score.

        Args:
            score (int): The user's score.

        Returns:
            str: The skill level ('beginner', 'intermediate', or 'advanced').
        """
        return 'beginner' if score <= 4 else 'intermediate' if score <= 12 else 'advanced'

        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Initialize new users with assessment option or welcome back existing users.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The context object storing user data.

        Returns:
            int: The next conversation state.
        """
        # context.user_data['current_question_index'] = 0
        # context.user_data['score'] = 0

        context.user_data.update({
            'current_question_index': 0,
            'score': 0
        })
        
        first_name = update.effective_user.first_name
        user_id = update.effective_user.id
        
        existing_user: tuple = self.db.get_users(user_id) # returns none if not exists
        if not existing_user: # user not in the db
            return await self._handle_new_user(update, first_name)
    
        await update.message.reply_text(text=f"Welcome back, {first_name}.")
        return ConvState.END_ASSESSMENT


    async def _handle_new_user(self, update: Update, first_name: str) -> int:
            msg = (
                f"Hello, {first_name}. I see this is the first time you use the bot.\n"
                f"How about you take an assessment to determine your level? "
                f"Our assessment has {len(initial_asses_qs)} questions."
            )
            reply_markup = self.create_keyboard(texts=["Yes, let's start!", "No, maybe later"],
                                                callbacks=["start_assessment", "decline_assessment"])
            await update.message.reply_text(text=msg, reply_markup=reply_markup)
            return ConvState.START


    async def _handle_stay(self, query, _):
        """Handle 'stay' button press."""
        await query.edit_message_text(text="We are glad to have you!")
        return ConvState.END_ASSESSMENT


    async def _handle_unsubscribe(self, query, _):
        self.db.delete_user(query.from_user.id)
        await query.edit_message_text(text="You have been unsubscribed.")
        return ConversationHandler.END


    async def _handle_start_assessment(self, query, context):
        await query.edit_message_text(text="Great! Let's begin the assessment.")
        first_question, _ = initial_asses_qs[0]
        await query.message.reply_text(first_question)
        context.user_data['current_question_index'] = 0
        context.user_data['score'] = 0
        return ConvState.QUESTION


    async def _handle_decline_assessment(self, query, _):
        await query.edit_message_text(text="Ok, you can start the assessment anytime.")
        return ConvState.END_ASSESSMENT


    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles inline button presses and updates the chat accordingly."""
        query = update.callback_query
        await query.answer()

        handlers = {
            "stay": self._handle_stay,
            "unsubscribe": self._handle_unsubscribe,
            "start_assessment": self._handle_start_assessment,
            "decline_assessment": self._handle_decline_assessment,
        }

        handler = handlers.get(query.data, lambda *args: ConvState.END_ASSESSMENT)
        return await handler(query, context)


        # if query.data == 'stay':
        #     logging.info("Stay button pressed")
        #     await query.edit_message_text(text="We are glad to have you!")
        #     return ConvState.END_ASSESSMENT.value
        
        # elif query.data == 'unsubscribe':
        #     user_id = update.effective_user.id
        #     self.db.delete_user(user_id)
        #     await query.edit_message_text(text="You have been unsubscribed.")
        #     return ConversationHandler.END

        # elif query.data == 'start_assessment':
        #     await query.edit_message_text(text="Great! Let's begin the assessment.")
        #     first_question, _ = initial_asses_qs[0]
        #     await query.message.reply_text(first_question)
        #     context.user_data['current_question_index'] = 0
        #     context.user_data['score'] = 0
        #     return ConvState.QUESTION.value
        
        # elif query.data == 'decline_assessment':
        #     await query.edit_message_text(text="Ok, you can start the assessment anytime.")
        #     return ConvState.END_ASSESSMENT.value
        
        # return ConvState.END_ASSESSMENT.value


    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Processes user answers during the assessment."""
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name
        user_answer = update.message.text

        current_index = context.user_data.get('current_question_index', 0)
        current_score = context.user_data.get('score', 0)

        if current_index >= len(initial_asses_qs):
            await update.message.reply_text("Assessment completed!")
            return ConvState.END_ASSESSMENT

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
            return ConvState.QUESTION
        else:
            level = self.level_by_score(current_score)
            self.db.insert_user(user_id, current_score, first_name, level)

            await update.message.reply_text(f"Assessment completed! Your level is: {level}")
            return ConvState.END_ASSESSMENT


    async def cancel_assessment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancels an ongoing assessment session."""
        await update.message.reply_text("Assessment cancelled.")
        return ConvState.END_ASSESSMENT
        

    async def insert_q(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inserts a new assessment question (admin only)."""
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

    
    async def delete_q(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Deletes an assessment question by ID (admin only)."""
        user_id = update.effective_user.id
        if user_id not in self.admins:
            await update.message.reply_text("Sorry, this command is only available for admins.")
            return

        q_id = context.args[0]
        self.db.delete_q(q_id)
        await update.message.reply_text(f" The question with id {q_id} is deleted.")


    async def ask_cohere(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles user queries and generates AI-based responses."""
        args = context.args
        question = ' '.join(args)
        msg = await update.message.reply_text('Thinking....')
        answer: str = self.teacher.get_response(question, user_asks=1)
        
        await msg.edit_text(answer)


    async def my_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Retrieves and displays the user's current learning level."""
        user_id = update.effective_user.id
        score_level = self.db.get_users(id=user_id) # returns (user_id, score, level)
        if score_level is None:
            await update.message.reply_text(f"Your are not subscribed to the bot.")
            return
        
        score, level = score_level[1], score_level[2]
        await update.message.reply_text(f"Your level is {level} with a score of {score}.")


    async def get_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Retrieves and displays all available assessment questions (admin only)."""
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
        """Initiates the process for a user to unsubscribe from the bot."""
        msg = "Are you sure you want to unsubscribe from the bot? ***All your records will be deleted***."
        reply_markup = self.create_keyboard(texts=["Yes, I'm sure", "No, I will stay"],
                                            callbacks=["unsubscribe", "stay"])
        await update.message.reply_text(text=msg, reply_markup=reply_markup, parse_mode='Markdown')


    async def top_learners(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Displays the top learners in a formatted table."""
        top_learners = self.db.get_top_learners()
        
        table_lines = ["🏆 Top Learners 🏆"]
        table_lines.append("```")
        table_lines.append(f"{'Name':<10} {'Level':<12} {'Score':<5}")
        table_lines.append("-" * 30)
        
        for name, level, score in top_learners:
            table_lines.append(f"{name:<10} {level:<12} {score:<5}")
        
        table_lines.append("```")
        
        await update.message.reply_text("\n".join(table_lines), parse_mode='Markdown')


    async def task_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Updates the frequency of task notifications."""
        user_id = update.effective_user.id
        interval = context.args[0]

        self.db.update_interval(user_id, interval)

        await update.message.reply_text(f"You will get a task every {interval} hours.")


    async def send_daily_task(self, context: ContextTypes.DEFAULT_TYPE):
        """Send daily tasks to users"""
        users = self.db.get_users(daily_task=True)
        current_time = datetime.now()

        for user_id, level, last_assessment, task_interval in users:
            if isinstance(last_assessment, str):
                last_assessment = datetime.strptime(last_assessment, "%Y-%m-%d %H:%M:%S.%f")

            time_diff = current_time - last_assessment

            if time_diff < timedelta(hours=task_interval):
                continue

            # Check if user already has an active question
            result = self.db.execute_query('''
                SELECT current_question 
                FROM users 
                WHERE user_id = ? AND current_question IS NOT NULL
            ''', (user_id,))
            
            if result:
                continue  # Skip if user already has an active question

            questions = self.db.get_questions(q_level=level)

            if not questions:
                logging.warning(f"No questions available for level: {level}")
                continue

            daily_question = random.choice(questions)[0]

            self.db.execute_query('''
                UPDATE users 
                SET current_question = ?,
                    last_assessment = ?
                WHERE user_id = ?
                ''', 
                (daily_question, current_time, user_id))
            
            message = (
                "🎯 Here's your daily Python challenge!\n\n"
                f"{daily_question}\n\n"
                "Reply with your answer or use /skip to skip this question."
            )
            
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='HTML'
                )
            except Exception as e:
                logging.error(f"Failed to send message to user {user_id}: {str(e)}")
                continue
            
            await asyncio.sleep(0.5)


    async def handle_daily_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle answers to daily tasks"""
        user_id = update.effective_user.id
        user_answer = update.message.text

        # Check if user has an active daily task
        result = self.db.execute_query('''
            SELECT current_question, score, level 
            FROM users 
            WHERE user_id = ? AND current_question IS NOT NULL
        ''', (user_id,))
        
        if not result:
            # No active daily task, let other handlers process the message
            return
        
        current_question, current_score, current_level = result[0]
        
        message = f"Question: {current_question}. User Answer: {user_answer}"
        status = self.teacher.get_response(message)
        score_change = score_weights.get(current_level, 1)

        if status == 1:
            new_score = current_score + score_change
            await update.message.reply_text(
                f"🎉 Correct! You earned {score_change} points.\n"
                f"Your new score is: {new_score}"
            )
        else:
            new_score = max(0, current_score - score_change)
            await update.message.reply_text(
                f"❌ That's not quite right. You lost {score_change} points.\n"
                f"Your new score is: {new_score}"
            )

        new_level = self.level_by_score(new_score)
        is_expert = new_level == 'advanced'
        self.db.execute_query('''
            UPDATE users 
            SET score = ?,
                current_question = NULL,
                last_assessment = ?,
                level = ?,
                is_expert = ?
            WHERE user_id = ?
        ''', (new_score, datetime.now(), new_level, is_expert, user_id))

        self.db.insert_assesment(
            user_id, 
            current_question, 
            user_answer, 
            status, 
            datetime.now()
        )


    async def skip_daily_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle skipping of daily tasks."""
        user_id = update.effective_user.id
        
        result = self.db.execute_query('''
            SELECT current_question 
            FROM users 
            WHERE user_id = ? AND current_question IS NOT NULL
        ''', (user_id,))
        
        if not result:
            await update.message.reply_text("You don't have an active daily task to skip!")
            return
        
        self.db.execute_query('''
            UPDATE users 
            SET current_question = NULL
            WHERE user_id = ?
        ''', (user_id,))
        
        await update.message.reply_text("Daily task skipped. Wait for the next one!")
    

    def run(self):
        logging.info("======== Bot is running ========")
        self.application.run_polling()

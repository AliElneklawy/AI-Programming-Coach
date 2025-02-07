# AI Programming Coach - Telegram Bot

## AI Programming Coach

**AI-Powered Telegram Bot for Personalized Programming Assessments and Exercises**

Try it out: @AI_Programming_Coach_bot

## Overview

AI Programming Coach is a Telegram bot designed to enhance users' programming skills through personalized assessments and daily exercises. It evaluates users' proficiency levels and provides tailored programming questions, enabling consistent practice and improvement.

## Features

### 1. **User Assessment & Level Evaluation**
- New users are prompted to take an assessment.
- The bot evaluates responses and assigns users one of three skill levels: `Beginner`, `Intermediate`, or `Advanced`.
- Assessment results are stored in a database to track progress.

### 2. **Daily Challenges**
- Users receive daily programming questions based on their skill level.
- Responses are evaluated, and scores are updated accordingly.
- Users can skip a daily challenge using the `/skip` command.

### 3. **Adaptive Learning System**
- Users' levels are dynamically updated based on their performance.
- Correct answers increase the score, while incorrect answers may result in score deductions.

### 4. **Admin Features**
- Admins can add and delete questions using `/insert_q` and `/delete_q` commands.
- Admins can retrieve all stored questions using `/get_questions`.

### 5. **Cohere AI Integration for Question Responses**
- Users can ask programming-related questions via `/ask_cohere`, and the bot will provide AI-generated answers.

### 6. **User Management**
- Users can check their current level and score using `/my_level`.
- The bot allows users to unsubscribe and delete their records via `/unsubscribe`.
- A `/top_learners` command displays the highest-scoring users.

## Installation & Setup

### Prerequisites
- Python 3.11
- Telegram Bot API Token
- SQLite for storing user data
- Cohere API key (for AI-generated answers)

### Steps to Run Locally

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/AliElneklawy/AI-Programming-Coach.git
   cd AI-Programming-Coach
   ```

2. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**  
   Create a `.env` file in the project directory and add:  
   ```
   BOT_TOKEN=your_telegram_bot_token
   COHERE_API_KEY=your_cohere_api_key
   ```

4. **Run the Bot**  
   ```bash
   python main.py
   ```

## Usage

### Commands for Users
| Command           | Description |
|------------------|-------------|
| `/start` | Starts the bot and prompts a programming assessment if first-time use. |
| `/my_level` | Displays the user’s current level and score. |
| `/skip` | Skips the daily challenge. |
| `/unsubscribe` | Deletes the user’s data and unsubscribes from the bot. |
| `/ask_cohere <question>` | Asks an AI-powered programming question. |
| `/top_learners` | Displays the leaderboard of top learners. |

### Commands for Admins
| Command | Description |
|---------|-------------|
| `/insert_q <question> <level>` | Adds a new question to the database. |
| `/delete_q <question_id>` | Removes a question from the database. |
| `/get_questions` | Retrieves all questions in the database. |


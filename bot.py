import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext
)
import os
from games.tictactoe import TicTacToeGame
from games.guess_number import NumberGame
from games.word_scramble import WordScrambleGame
from games.trivia import TriviaGame
from games.hangman import HangmanGame
from games.memory import MemoryGame
from games.rps import RPSGame
from games.math_challenge import MathGame
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ.get('TOKEN')

class GameBot:
    def __init__(self):
        self.games = {
            'tictactoe': TicTacToeGame(),
            'number': NumberGame(),
            'scramble': WordScrambleGame(),
            'trivia': TriviaGame(),
            'hangman': HangmanGame(),
            'memory': MemoryGame(),
            'rps': RPSGame(),
            'math': MathGame()
        }
        self.active_games = {}
        self.scores = {}
        self.daily_scores = {}

    async def start(self, update: Update, context: CallbackContext) -> None:
        """Send message on `/start`."""
        user = update.message.from_user
        logger.info("User %s started the bot.", user.first_name)

        keyboard = [
            [
                InlineKeyboardButton("Tic Tac Toe", callback_data='tictactoe'),
                InlineKeyboardButton("Guess Number", callback_data='number'),
            ],
            [
                InlineKeyboardButton("Word Scramble", callback_data='scramble'),
                InlineKeyboardButton("Trivia Quiz", callback_data='trivia'),
            ],
            [
                InlineKeyboardButton("Hangman", callback_data='hangman'),
                InlineKeyboardButton("Memory Match", callback_data='memory'),
            ],
            [
                InlineKeyboardButton("Rock Paper Scissors", callback_data='rps'),
                InlineKeyboardButton("Math Challenge", callback_data='math'),
            ],
            [
                InlineKeyboardButton("🏆 Leaderboard", callback_data='leaderboard'),
                InlineKeyboardButton("🌟 Daily Challenge", callback_data='daily')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"🎮 *Welcome to Game Boat, {user.first_name}!* 🚢\n\n"
            "⚡ Choose from 8 exciting games:\n\n"
            "🔴 *Tic Tac Toe* - Classic X and O game\n"
            "🔵 *Guess Number* - Find the secret number\n"
            "🟢 *Word Scramble* - Unscramble the word\n"
            "🟡 *Trivia Quiz* - Test your knowledge\n"
            "🟣 *Hangman* - Guess the word letter by letter\n"
            "🟠 *Memory Match* - Find matching pairs\n"
            "⚪ *Rock Paper Scissors* - Classic hand game\n"
            "🟤 *Math Challenge* - Solve math problems fast\n\n"
            "Click a button below to start playing!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button(self, update: Update, context: CallbackContext) -> None:
        """Handle button presses."""
        query = update.callback_query
        await query.answer()

        if query.data == 'back':
            return await self.start_callback(update, context)
        
        if query.data == 'leaderboard':
            return await self.show_leaderboard(update, context)
            
        if query.data == 'daily':
            return await self.show_daily_challenge(update, context)

        game_type = query.data
        chat_id = query.message.chat_id
        user_id = query.from_user.id

        if game_type in self.games:
            if game_type not in self.active_games:
                self.active_games[game_type] = {}

            if chat_id not in self.active_games[game_type]:
                self.active_games[game_type][chat_id] = self.games[game_type].new_game()

            game = self.active_games[game_type][chat_id]
            response = await self.games[game_type].handle_message(update, context, game)
            
            if response and 'points' in response:
                if chat_id not in self.scores:
                    self.scores[chat_id] = {}
                self.scores[chat_id][user_id] = self.scores[chat_id].get(user_id, 0) + response['points']
            
            if response and 'text' in response:
                await query.edit_message_text(**response)
        else:
            await query.edit_message_text(text="Invalid game selection. Please try again.")

    async def show_leaderboard(self, update: Update, context: CallbackContext) -> None:
        """Display the leaderboard."""
        query = update.callback_query
        chat_id = query.message.chat_id
        
        if chat_id in self.scores and self.scores[chat_id]:
            sorted_scores = sorted(
                self.scores[chat_id].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            leaderboard_text = "🏆 *Leaderboard* 🏆\n\n"
            for i, (user_id, score) in enumerate(sorted_scores[:10]):
                try:
                    user = await context.bot.get_chat_member(chat_id, user_id)
                    leaderboard_text += f"{i+1}. {user.user.first_name}: {score} points\n"
                except:
                    leaderboard_text += f"{i+1}. User {user_id}: {score} points\n"
        else:
            leaderboard_text = "No scores yet! Play some games first."
        
        keyboard = [[InlineKeyboardButton("Back to Menu", callback_data='back')]]
        await query.edit_message_text(
            text=leaderboard_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def show_daily_challenge(self, update: Update, context: CallbackContext) -> None:
        """Show the daily challenge status."""
        query = update.callback_query
        today = datetime.now().date()
        
        if today not in self.daily_scores:
            self.daily_scores[today] = {}
        
        if self.daily_scores[today]:
            sorted_scores = sorted(
                self.daily_scores[today].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            challenge_text = "🌟 *Daily Challenge* 🌟\n\n"
            for i, (user_id, score) in enumerate(sorted_scores[:5]):
                try:
                    user = await context.bot.get_chat_member(query.message.chat_id, user_id)
                    challenge_text += f"{i+1}. {user.user.first_name}: {score} points\n"
                except:
                    challenge_text += f"{i+1}. User {user_id}: {score} points\n"
        else:
            challenge_text = "No daily challenge scores yet! Be the first to play today."
        
        keyboard = [[InlineKeyboardButton("Back to Menu", callback_data='back')]]
        await query.edit_message_text(
            text=challenge_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def start_callback(self, update: Update, context: CallbackContext) -> None:
        """Handle the back to start callback."""
        query = update.callback_query
        await self.start(update, context)
        await query.delete_message()

    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text(
            "🚀 *Game Boat Help* 🚀\n\n"
            "Available commands:\n"
            "/start - Show the game menu\n"
            "/help - Show this help message\n"
            "/leaderboard - Show top players\n"
            "/daily - Show daily challenge\n\n"
            "Game Instructions:\n"
            "- Click any game button to start\n"
            "- Each game has its own rules\n"
            "- Play with friends in group chats\n\n"
            "Have fun! 🎉",
            parse_mode='Markdown'
        )

    async def leaderboard_command(self, update: Update, context: CallbackContext) -> None:
        """Handle the /leaderboard command."""
        await self.show_leaderboard(update, context)

    async def daily_command(self, update: Update, context: CallbackContext) -> None:
        """Handle the /daily command."""
        await self.show_daily_challenge(update, context)

async def post_init(application):
    await application.bot.set_my_commands([
        ("start", "Start the bot"),
        ("help", "Show help"),
        ("leaderboard", "Show leaderboard"),
        ("daily", "Daily challenge")
    ])

def main() -> None:
    """Run the bot."""
    game_bot = GameBot()
    
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", game_bot.start))
    application.add_handler(CommandHandler("help", game_bot.help_command))
    application.add_handler(CommandHandler("leaderboard", game_bot.leaderboard_command))
    application.add_handler(CommandHandler("daily", game_bot.daily_command))
    application.add_handler(CallbackQueryHandler(game_bot.button))

    # Start the Bot
    if os.environ.get('ENV') == 'PRODUCTION':
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=os.environ.get('WEBHOOK_URL')
        )
    else:
        application.run_polling()

if __name__ == '__main__':
    main()

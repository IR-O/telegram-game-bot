from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import random

WORDS = [
    "PYTHON", "TELEGRAM", "BOT", "PROGRAMMING", "DEVELOPER",
    "KEYBOARD", "MONITOR", "COMPUTER", "ALGORITHM", "FUNCTION",
    "VARIABLE", "STRING", "INTEGER", "BOOLEAN", "DICTIONARY"
]

class WordScrambleGame:
    async def new_game(self):
        word = random.choice(WORDS)
        scrambled = ''.join(random.sample(word, len(word)))
        return {
            'original_word': word,
            'scrambled_word': scrambled,
            'attempts': 0,
            'hints_used': 0,
            'message_id': None
        }

    async def handle_message(self, update: Update, context: CallbackContext, game):
        query = update.callback_query
        data = query.data.split('_')[-1] if '_' in query.data else None

        if data == 'start':
            game.update(await self.new_game())
            return await self.render_game(game, f"Unscramble this word: {game['scrambled_word']}")
        
        elif data == 'hint':
            game['hints_used'] += 1
            hint = game['original_word'][:game['hints_used']] + '_' * (len(game['original_word']) - game['hints_used'])
            return await self.render_game(
                game,
                f"Unscramble this word: {game['scrambled_word']}\n"
                f"Hint: {hint} (Hints used: {game['hints_used']})"
            )
        
        elif data == 'back':
            return None
        
        elif data == 'solve':
            return await self.render_game(
                game,
                f"The word was: {game['original_word']}\n"
                f"You used {game['hints_used']} hints.",
                game_over=True
            )
        
        elif data and data.isalpha():
            game['attempts'] += 1
            if data.upper() == game['original_word']:
                points = max(15 - game['hints_used'] * 3, 1)
                return {
                    **await self.render_game(
                        game,
                        f"🎉 Correct! The word was {game['original_word']}!\n"
                        f"You solved it in {game['attempts']} attempts with {game['hints_used']} hints.",
                        game_over=True
                    ),
                    'points': points
                }
            else:
                return await self.render_game(
                    game,
                    f"❌ Incorrect! Try again.\n"
                    f"Unscramble this word: {game['scrambled_word']}\n"
                    f"Attempts: {game['attempts']}"
                )
        else:
            return await self.render_game(game, f"Unscramble this word: {game['scrambled_word']}")

    async def render_game(self, game, message, game_over=False):
        if game_over:
            keyboard = [
                [InlineKeyboardButton("Play Again", callback_data='scramble_start')],
                [InlineKeyboardButton("Back to Menu", callback_data='back')]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Get Hint", callback_data='scramble_hint')],
                [InlineKeyboardButton("Give Up", callback_data='scramble_solve')],
                [InlineKeyboardButton("Back to Menu", callback_data='back')]
            ]
        
        return {
            'text': f"🔠 *WORD SCRAMBLE* 🔤\n\n{message}",
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

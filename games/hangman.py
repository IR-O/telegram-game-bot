from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import random

WORDS = [
    "PYTHON", "JAVASCRIPT", "TELEGRAM", "DEVELOPER", "PROGRAMMING",
    "KEYBOARD", "MONITOR", "COMPUTER", "ALGORITHM", "FUNCTION"
]

HANGMAN_STAGES = [
    """
     -----
     |   |
         |
         |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
         |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
     |   |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
    /|   |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
    /|\\  |
         |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
    /|\\  |
    /    |
         |
    --------
    """,
    """
     -----
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    --------
    """
]

class HangmanGame:
    def new_game(self):
        word = random.choice(WORDS)
        return {
            'word': word,
            'guessed': ['_' for _ in word],
            'wrong_guesses': [],
            'stage': 0,
            'message_id': None
        }

    def handle_message(self, update: Update, context: CallbackContext, game):
        query = update.callback_query
        data = query.data.split('_')[-1] if '_' in query.data else None

        if data == 'start':
            game.update(self.new_game())
            return self.render_game(game, "Guess a letter to save the hangman!")
        
        elif data == 'back':
            return None
        
        elif data and data.isalpha() and len(data) == 1:
            letter = data.upper()
            
            if letter in game['wrong_guesses'] or letter in game['guessed']:
                query.answer(text="You already guessed that letter!", show_alert=True)
                return None
            
            if letter in game['word']:
                for i, char in enumerate(game['word']):
                    if char == letter:
                        game['guessed'][i] = letter
                
                if '_' not in game['guessed']:
                    return self.render_game(
                        game,
                        f"🎉 You won! The word was: {game['word']}",
                        game_over=True
                    )
                return self.render_game(game, "Correct! Guess another letter.")
            else:
                game['wrong_guesses'].append(letter)
                game['stage'] += 1
                
                if game['stage'] >= len(HANGMAN_STAGES) - 1:
                    return self.render_game(
                        game,
                        f"💀 Game Over! The word was: {game['word']}",
                        game_over=True
                    )
                return self.render_game(game, "Wrong guess! Try again.")
        else:
            return self.render_game(game, "Guess a letter to save the hangman!")

    def render_game(self, game, message, game_over=False):
        # Create alphabet keyboard
        keyboard = []
        row = []
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if letter in game['wrong_guesses'] or letter in game['guessed']:
                row.append(InlineKeyboardButton("❌", callback_data=f"hangman_{letter}"))
            else:
                row.append(InlineKeyboardButton(letter, callback_data=f"hangman_{letter}"))
            if len(row) == 7:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        if game_over:
            keyboard.append([InlineKeyboardButton("Play Again", callback_data='hangman_start')])
        keyboard.append([InlineKeyboardButton("Back to Menu", callback_data='back')])
        
        return {
            'text': (
                f"💀 *HANGMAN* 💀\n\n"
                f"{HANGMAN_STAGES[game['stage']]}\n"
                f"Word: {' '.join(game['guessed'])}\n"
                f"Wrong guesses: {', '.join(game['wrong_guesses']) or 'None'}\n\n"
                f"{message}"
            ),
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

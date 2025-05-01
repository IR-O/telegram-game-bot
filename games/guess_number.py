from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import random

class NumberGame:
    async def new_game(self):
        return {
            'secret_number': random.randint(1, 100),
            'attempts': 0,
            'min_range': 1,
            'max_range': 100,
            'message_id': None
        }

    async def handle_message(self, update: Update, context: CallbackContext, game):
        query = update.callback_query
        data = query.data.split('_')[-1] if '_' in query.data else None

        if data == 'start':
            game.update(await self.new_game())
            return await self.render_game(game, "I've picked a number between 1-100. Guess it!")
        
        elif data == 'back':
            return None
        
        elif data and data.isdigit():
            guess = int(data)
            game['attempts'] += 1
            
            if guess == game['secret_number']:
                points = max(10 - game['attempts'], 1)
                return {
                    **await self.render_game(
                        game,
                        f"🎉 Correct! You guessed it in {game['attempts']} attempts!\n"
                        f"The number was {game['secret_number']}.",
                        game_over=True
                    ),
                    'points': points
                }
            elif guess < game['secret_number']:
                game['min_range'] = guess + 1
                hint = "⬆️ Higher!"
            else:
                game['max_range'] = guess - 1
                hint = "⬇️ Lower!"
            
            return await self.render_game(
                game,
                f"{hint} The number is between {game['min_range']}-{game['max_range']}.\n"
                f"Attempts: {game['attempts']}"
            )
        else:
            return await self.render_game(game, "Guess the number between 1-100:")

    async def render_game(self, game, message, game_over=False):
        if game_over:
            keyboard = [
                [InlineKeyboardButton("Play Again", callback_data='number_start')],
                [InlineKeyboardButton("Back to Menu", callback_data='back')]
            ]
        else:
            keyboard = []
            row = []
            for num in range(game['min_range'], game['max_range'] + 1):
                if len(row) == 5:
                    keyboard.append(row)
                    row = []
                row.append(InlineKeyboardButton(str(num), callback_data=f"number_{num}"))
            if row:
                keyboard.append(row)
            
            keyboard.append([InlineKeyboardButton("Back to Menu", callback_data='back')])
        
        return {
            'text': f"🔢 *GUESS THE NUMBER* 🔢\n\n{message}",
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

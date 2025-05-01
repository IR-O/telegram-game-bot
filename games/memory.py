from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, JobQueue
import random

class MemoryGame:
    async def new_game(self):
        emojis = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"]
        pairs = emojis * 2
        random.shuffle(pairs)
        
        return {
            'cards': pairs,
            'revealed': [False] * len(pairs),
            'first_card': None,
            'matches': 0,
            'moves': 0,
            'message_id': None
        }

    async def handle_message(self, update: Update, context: CallbackContext, game):
        query = update.callback_query
        data = query.data.split('_')[-1] if '_' in query.data else None

        if data == 'start':
            game.update(await self.new_game())
            return await self.render_game(game, "Find all matching pairs!")
        
        elif data == 'back':
            return None
        
        elif data and data.isdigit():
            card_index = int(data)
            
            if game['revealed'][card_index] or card_index == game['first_card']:
                await query.answer(text="Invalid selection!", show_alert=True)
                return None
            
            game['revealed'][card_index] = True
            game['moves'] += 1
            
            if game['first_card'] is None:
                game['first_card'] = card_index
                return await self.render_game(game, "Select another card to find a match.")
            else:
                first_card = game['first_card']
                if game['cards'][first_card] == game['cards'][card_index]:
                    game['matches'] += 1
                    if game['matches'] == len(game['cards']) // 2:
                        points = max(20 - game['moves'], 5)
                        return {
                            **await self.render_game(
                                game,
                                f"🎉 You won in {game['moves']} moves!",
                                game_over=True
                            ),
                            'points': points
                        }
                    game['first_card'] = None
                    return await self.render_game(game, "Match found! Keep going.")
                else:
                    context.job_queue.run_once(
                        lambda ctx: self.hide_cards(update, context, game, first_card, card_index),
                        2
                    )
                    return await self.render_game(game, "No match, try again!")

        return await self.render_game(game, "Find all matching pairs!")

    async def hide_cards(self, update: Update, context: CallbackContext, game, card1, card2):
        game['revealed'][card1] = False
        game['revealed'][card2] = False
        game['first_card'] = None
        await self.render_game(game, "Cards hidden. Try again!")

    async def render_game(self, game, message, game_over=False):
        keyboard = []
        row = []
        for i, (card, revealed) in enumerate(zip(game['cards'], game['revealed'])):
            if revealed or game_over:
                row.append(InlineKeyboardButton(card, callback_data=f"memory_{i}"))
            else:
                row.append(InlineKeyboardButton("❓", callback_data=f"memory_{i}"))
            
            if len(row) == 4:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        if game_over:
            keyboard.append([InlineKeyboardButton("Play Again", callback_data='memory_start')])
        keyboard.append([InlineKeyboardButton("Back to Menu", callback_data='back')])
        
        return {
            'text': (
                f"🧠 *MEMORY MATCH* 🧠\n\n"
                f"Matches found: {game['matches']}/{len(game['cards'])//2}\n"
                f"Moves: {game['moves']}\n\n"
                f"{message}"
            ),
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

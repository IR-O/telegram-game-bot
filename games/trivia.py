from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import random

TRIVIA_QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct": 2,
        "category": "Geography"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct": 1,
        "category": "Science"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Vincent van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Michelangelo"],
        "correct": 2,
        "category": "Art"
    },
    {
        "question": "What is the largest mammal?",
        "options": ["Elephant", "Blue Whale", "Giraffe", "Polar Bear"],
        "correct": 1,
        "category": "Science"
    },
    {
        "question": "In which year did World War II end?",
        "options": ["1943", "1945", "1947", "1950"],
        "correct": 1,
        "category": "History"
    }
]

class TriviaGame:
    async def new_game(self):
        question = random.choice(TRIVIA_QUESTIONS)
        return {
            'question': question['question'],
            'options': question['options'],
            'correct': question['correct'],
            'category': question['category'],
            'answered': False,
            'message_id': None
        }

    async def handle_message(self, update: Update, context: CallbackContext, game):
        query = update.callback_query
        data = query.data.split('_')[-1] if '_' in query.data else None

        if data == 'start':
            game.update(await self.new_game())
            return await self.render_game(game, game['question'])
        
        elif data == 'back':
            return None
        
        elif data and data.isdigit():
            selected = int(data)
            if game['answered']:
                await query.answer(text="This question has already been answered!", show_alert=True)
                return None
            
            game['answered'] = True
            if selected == game['correct']:
                return {
                    **await self.render_game(
                        game,
                        f"✅ Correct! {game['options'][game['correct']]} is the right answer.",
                        answered=True
                    ),
                    'points': 5
                }
            else:
                return await self.render_game(
                    game,
                    f"❌ Wrong! The correct answer is {game['options'][game['correct']]}.\n"
                    f"You selected {game['options'][selected]}.",
                    answered=True
                )
        else:
            return await self.render_game(game, game['question'])

    async def render_game(self, game, message, answered=False):
        keyboard = []
        for i, option in enumerate(game['options']):
            if answered:
                prefix = "✅ " if i == game['correct'] else "❌ "
                keyboard.append([InlineKeyboardButton(prefix + option, callback_data=f"trivia_{i}")])
            else:
                keyboard.append([InlineKeyboardButton(option, callback_data=f"trivia_{i}")])
        
        if answered:
            keyboard.append([InlineKeyboardButton("Next Question", callback_data='trivia_start')])
        keyboard.append([InlineKeyboardButton("Back to Menu", callback_data='back')])
        
        return {
            'text': f"❓ *TRIVIA QUIZ* ({game['category']}) ❓\n\n{message}",
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

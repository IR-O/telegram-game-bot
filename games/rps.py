from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import random

CHOICES = ["🪨 Rock", "📄 Paper", "✂️ Scissors"]
OUTCOMES = {
    ("🪨 Rock", "✂️ Scissors"): "Rock crushes Scissors",
    ("📄 Paper", "🪨 Rock"): "Paper covers Rock",
    ("✂️ Scissors", "📄 Paper"): "Scissors cut Paper"
}

class RPSGame:
    def new_game(self):
        return {
            'player_choice': None,
            'bot_choice': None,
            'score': [0, 0],  # [player, bot]
            'message_id': None
        }

    def handle_message(self, update: Update, context: CallbackContext, game):
        query = update.callback_query
        data = query.data.split('_')[-1] if '_' in query.data else None

        if data == 'start':
            game.update(self.new_game())
            return self.render_game(game, "Choose Rock, Paper, or Scissors!")
        
        elif data == 'back':
            return None
        
        elif data in ['0', '1', '2']:
            player_choice = CHOICES[int(data)]
            bot_choice = random.choice(CHOICES)
            game['player_choice'] = player_choice
            game['bot_choice'] = bot_choice
            
            if player_choice == bot_choice:
                result = "It's a tie!"
            else:
                if (player_choice, bot_choice) in OUTCOMES:
                    game['score'][0] += 1
                    result = f"You win! {OUTCOMES[(player_choice, bot_choice)]}"
                    points = 3
                else:
                    game['score'][1] += 1
                    result = f"You lose! {OUTCOMES[(bot_choice, player_choice)]}"
                    points = 0
            
            return {
                **self.render_game(
                    game,
                    f"You chose: {player_choice}\n"
                    f"Bot chose: {bot_choice}\n\n"
                    f"{result}\n"
                    f"Score: You {game['score'][0]} - {game['score'][1]} Bot"
                ),
                'points': points
            }
        else:
            return self.render_game(game, "Choose Rock, Paper, or Scissors!")

    def render_game(self, game, message):
        keyboard = [
            [
                InlineKeyboardButton("🪨 Rock", callback_data='rps_0'),
                InlineKeyboardButton("📄 Paper", callback_data='rps_1'),
                InlineKeyboardButton("✂️ Scissors", callback_data='rps_2'),
            ],
            [InlineKeyboardButton("Back to Menu", callback_data='back')]
        ]
        
        return {
            'text': f"🪨📄✂️ *ROCK PAPER SCISSORS* ✂️📄🪨\n\n{message}",
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

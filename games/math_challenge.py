from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, JobQueue
import random
import operator
from datetime import datetime

OPERATIONS = {
    '+': operator.add,
    '-': operator.sub,
    '×': operator.mul,
    '÷': operator.truediv
}

class MathGame:
    def new_game(self):
        op = random.choice(list(OPERATIONS.keys()))
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        
        # Ensure division problems have integer results
        if op == '÷':
            num1 = num1 * num2
        
        answer = OPERATIONS[op](num1, num2)
        
        return {
            'problem': f"{num1} {op} {num2}",
            'answer': answer,
            'options': self.generate_options(answer),
            'time_left': 30,
            'score': 0,
            'message_id': None,
            'job': None
        }

    def generate_options(self, correct_answer):
        options = [correct_answer]
        while len(options) < 4:
            option = correct_answer + random.randint(-5, 5)
            if option != correct_answer and option not in options and option > 0:
                options.append(option)
        random.shuffle(options)
        return options

    def handle_message(self, update: Update, context: CallbackContext, game):
        query = update.callback_query
        data = query.data.split('_')[-1] if '_' in query.data else None

        if data == 'start':
            # Cancel previous timer if exists
            if game.get('job'):
                game['job'].schedule_removal()
            
            game.update(self.new_game())
            game['job'] = context.job_queue.run_repeating(
                self.update_timer,
                interval=1,
                first=1,
                context=(update.effective_chat.id, game)
            )
            return self.render_game(game, "Solve the math problem!")
        
        elif data == 'back':
            if game.get('job'):
                game['job'].schedule_removal()
            return None
        
        elif data and data.replace('.', '').isdigit():
            selected = float(data)
            if selected == game['answer']:
                game['score'] += 5
                game.update(self.new_game())
                return {
                    **self.render_game(game, "✅ Correct! Next problem:"),
                    'points': 5
                }
            else:
                return self.render_game(game, "❌ Wrong! Try again.")
        else:
            return self.render_game(game, "Solve the math problem!")

    def update_timer(self, context: CallbackContext):
        chat_id, game = context.job.context
        game['time_left'] -= 1
        
        if game['time_left'] <= 0:
            game['time_left'] = 0
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=game['message_id'],
                text=(
                    f"⏰ *TIME'S UP!* ⏰\n\n"
                    f"Final Score: {game['score']}\n"
                    f"Last Problem: {game['problem']} = {game['answer']}\n\n"
                    "Click 'Play Again' to restart!"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Play Again", callback_data='math_start')],
                    [InlineKeyboardButton("Back to Menu", callback_data='back')]
                ]),
                parse_mode='Markdown'
            )
            context.job.schedule_removal()
            return

        # Update the message with remaining time
        try:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=game['message_id'],
                text=(
                    f"🧮 *MATH CHALLENGE* 🧮\n\n"
                    f"Score: {game['score']}\n"
                    f"Time left: {game['time_left']}s\n\n"
                    f"Problem: {game['problem']} = ?"
                ),
                reply_markup=self.generate_options_markup(game['options']),
                parse_mode='Markdown'
            )
        except:
            pass

    def generate_options_markup(self, options):
        keyboard = []
        row = []
        for option in options:
            row.append(InlineKeyboardButton(str(option), callback_data=f"math_{option}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("Back to Menu", callback_data='back')])
        return InlineKeyboardMarkup(keyboard)

    def render_game(self, game, message):
        if game['time_left'] <= 0:
            return {
                'text': (
                    f"⏰ *TIME'S UP!* ⏰\n\n"
                    f"Final Score: {game['score']}\n"
                    f"Last Problem: {game['problem']} = {game['answer']}\n\n"
                    "Click 'Play Again' to restart!"
                ),
                'reply_markup': InlineKeyboardMarkup([
                    [InlineKeyboardButton("Play Again", callback_data='math_start')],
                    [InlineKeyboardButton("Back to Menu", callback_data='back')]
                ]),
                'parse_mode': 'Markdown'
            }
        
        return {
            'text': (
                f"🧮 *MATH CHALLENGE* 🧮\n\n"
                f"Score: {game['score']}\n"
                f"Time left: {game['time_left']}s\n\n"
                f"Problem: {game['problem']} = ?\n\n"
                f"{message}"
            ),
            'reply_markup': self.generate_options_markup(game['options']),
            'parse_mode': 'Markdown'
        }

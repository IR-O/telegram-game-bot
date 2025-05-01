from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

class TicTacToeGame:
    def new_game(self):
        return {
            'board': [[' ' for _ in range(3)] for _ in range(3)],
            'players': ['❌', '⭕'],
            'current_player': 0,
            'message_id': None
        }

    def handle_message(self, update: Update, context: CallbackContext, game):
        query = update.callback_query
        data = query.data.split('_')[-1] if '_' in query.data else None

        if data == 'start':
            game.update(self.new_game())
            return self.render_board(game, f"Player {game['players'][game['current_player']]}'s turn")
        
        if data and data.isdigit():
            move = int(data)
            row, col = divmod(move - 1, 3)
            
            if game['board'][row][col] == ' ':
                game['board'][row][col] = game['players'][game['current_player']]
                
                winner = self.check_winner(game['board'])
                if winner:
                    return {
                        **self.render_board(game, f"🎉 Player {winner} wins!"),
                        'points': 10  # Award points for winning
                    }
                
                if self.is_board_full(game['board']):
                    return self.render_board(game, "🤝 It's a draw!")
                
                game['current_player'] = 1 - game['current_player']
                return self.render_board(game, f"Player {game['players'][game['current_player']]}'s turn")
            else:
                query.answer(text="That spot is already taken!", show_alert=True)
                return None
        else:
            return self.render_board(game, f"Player {game['players'][game['current_player']]}'s turn")

    def render_board(self, game, message):
        keyboard = []
        for i in range(3):
            row = []
            for j in range(3):
                row.append(InlineKeyboardButton(
                    game['board'][i][j] if game['board'][i][j] != ' ' else '⬜',
                    callback_data=f"tictactoe_{i*3 + j + 1}"
                ))
            keyboard.append(row)
        
        keyboard.append([
            InlineKeyboardButton("New Game", callback_data='tictactoe_start'),
            InlineKeyboardButton("Back to Menu", callback_data='back')
        ])
        
        return {
            'text': f"⭕ *TIC TAC TOE* ❌\n\n{message}",
            'reply_markup': InlineKeyboardMarkup(keyboard),
            'parse_mode': 'Markdown'
        }

    def check_winner(self, board):
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] != ' ':
                return row[0]
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != ' ':
                return board[0][col]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return board[0][2]
        
        return None

    def is_board_full(self, board):
        return all(cell != ' ' for row in board for cell in row)

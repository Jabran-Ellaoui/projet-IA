import random
from config import *
from sqlalchemy import Null, nullsfirst, false
from .models import *
from views import *
from .viewsFunctions import *
from ai import *
from colorama import Fore, Back, Style, init


def create_ai_players(db):
    ai1 = Player.query.filter_by(name="AI-1").first()
    ai2 = Player.query.filter_by(name="AI-2").first()
   
    if not ai1:
        player1 = Player(name="AI-1", is_human=False)
        db.session.add(ai1)
        db.session.commit()  

    if not ai2:
        player2 = Player(name="AI-2", is_human=False)
        db.session.add(ai2)
        db.session.commit()

    return ai1, ai2


def create_game(db, ai1, ai2):

    new_game = Game(player1_id=ai1.id_player, player2_id=ai2.id_player, table_size=TABLE_SIZE)
    db.session.add(new_game)
    db.session.commit()

    return new_game



def run_game(game, db, ai1, ai2):

    board = game.boxes

    winner = check_winner(game.boxes)
    turn_count = 0

    while not winner and turn_count < MAX_TURNS:
        turn_count += 1
        
        if game.current_player == game.player1_id:
            player_x = game.playerpos1_x
            player_y = game.playerpos1_y
            symbol = "1"
        else:
            player_x = game.playerpos2_x
            player_y = game.playerpos2_y
            symbol = "2"

        possibles_moves = valides_possibles_moves(board, {"x": player_x, "y": player_y, "symbol": symbol})
        move = get_move(game, possibles_moves, EPSILON, ALPHA, GAMMA)
        move_dict = MOVE[move]
        
        player_new_x, player_new_y, new_board = apply_movement(move_dict, board, {"x": player_x, "y": player_y, "symbol": symbol})
        checkBoard()

        board = game.boxes
        winner = check_winner(board)

        if winner == 0:
            print(f"Partie inachevée ou bloquée après {turn_count} tours.")
        else:
            print(f"Partie terminée en {turn_count} tours, vainqueur = {winner}.")
    db.session.commit()  # Sauver l'état final en base

        



    



if __name__ == "__main__":
    pass
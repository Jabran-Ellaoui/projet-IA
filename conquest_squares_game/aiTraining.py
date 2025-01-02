import random

from sqlalchemy import Null, nullsfirst, false
from .models import *
from .viewsFunctions import *
from .views import *
from .ai import *
from config import *
from colorama import Fore, Back, Style, init
import csv



def create_ai_players(db):
    ai1 = Player.query.filter_by(name="AI-1").first()
    ai2 = Player.query.filter_by(name="AI-2").first()
    randomAi = Player.query.filter_by(name="Random-AI").first()
   
    if not ai1:
        ai1 = Player(name="AI-1", is_human=False)
        db.session.add(ai1)
        db.session.commit()  

    if not ai2:
        ai2 = Player(name="AI-2", is_human=False)
        db.session.add(ai2)
        db.session.commit()
   
    if not randomAi:
        randomAi = Player(name="Random-AI", is_human=False)
        db.session.add(randomAi)
        db.session.commit()  


    return ai1, ai2, randomAi


def create_game(ai1, ai2):

    new_game = Game(player1_id=ai1.id_player, player2_id=ai2.id_player, table_size=TABLE_SIZE)
    db.session.add(new_game)
    db.session.commit()
    return new_game



def run_game(game, id_random_player):

    board = game.boxes

    winner = check_winner(game.boxes)
    turn_count = 0
    print(Fore.YELLOW + f"[INFO] : Lancement de la game id : {game.id_game} ")

    while not winner and turn_count < MAX_TURNS:
        turn_count += 1
        winner = check_winner(board)
        if game.current_player == game.player1_id:
            player_x = game.playerpos1_x
            player_y = game.playerpos1_y
            symbol = "1"
        else:
            player_x = game.playerpos2_x
            player_y = game.playerpos2_y
            symbol = "2"

        adaptedEpsilon = 1 if game.current_player == id_random_player  else EPSILON
        
        possibles_moves = valides_possibles_moves(board, {"x": player_x, "y": player_y, "symbol": symbol})
        move = get_move(game, possibles_moves, EPSILON, ALPHA, GAMMA, turn_count)
        move_dict = MOVE[move]

        player_new_x, player_new_y, new_board = apply_movement(move_dict, board, {"x": player_x, "y": player_y, "symbol": symbol})

        if game.current_player == game.player1_id:
            game.playerpos1_x = player_new_x
            game.playerpos1_y = player_new_y
        else:
            game.playerpos2_x = player_new_x
            game.playerpos2_y = player_new_y

        updatedBoard = checkBoardAI(new_board)
        board = updatedBoard
        game.boxes = board
        
        game.current_player = game.player1_id if game.current_player == game.player2_id else game.player2_id
        db.session.commit()
    
    if winner == 0:
        print(Fore.RED + f"Partie inachevée ou bloquée après {turn_count} tours.")
    else:
        print(Fore.GREEN + f"Partie terminée en {turn_count} tours, vainqueur = {winner}.")
    return winner, turn_count


def start_training():
    # Ouverture de fichier
    init_db()
    nbGames = 0
    ai1, ai2, randomAi = create_ai_players(db)
    game = create_game(ai1, ai2)

    while game.id_game < 100:
        winner, turn_count = run_game(game, randomAi)
        nbGames += 1
        game = create_game(ai1, ai2)

        if nbGames % 10 == 0:
            print(Fore.RED + "[INFO] : Lancement de la phase d'entraînement")
            nbGame = 0

            # Création du fichier CSV
            with open("training_phase.csv", "w", newline="") as csvfile:
                fieldnames = ["game_id", "winner_id", "turn_count"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                while nbGame < 10:
                    players = [ai1, randomAi]
                    player1 = random.choice(players)
                    player2 = ai1 if player1 == randomAi else randomAi
                    winner, turn_count = run_game(game, randomAi.id_player)

                    # Écrire les résultats de chaque partie dans le fichier CSV
                    writer.writerow({
                        "game_id": game.id_game,
                        "Winner" : winner,
                        "turn_count": turn_count
                    })

                    nbGame += 1
                    game = create_game(player1, player2)

            print(Fore.RED + "[INFO] : Fin de la phase d'entraînement")
            


            
        


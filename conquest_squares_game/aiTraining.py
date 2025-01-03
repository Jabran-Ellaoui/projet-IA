import random

from sqlalchemy import Null, nullsfirst, false
from .models import *
from .viewsFunctions import *
from .views import *
from .ai import *
from config import *
from colorama import Fore, Back, Style, init
import csv

def next_epsilon(epsilon,coef=0.99995, min=0.05):
    """
Met à jour la valeur d'epsilon pour contrôler l'équilibre entre exploration et exploitation.

Args:
    epsilon (float): La valeur actuelle d'epsilon.
    coef (float, optional): Facteur de réduction d'epsilon à chaque étape. Par défaut, 0.99995.
    min (float, optional): Valeur minimale d'epsilon pour éviter une réduction excessive. Par défaut, 0.05.

Returns:
    float: La nouvelle valeur d'epsilon.
"""
    epsilon = max(epsilon*coef, min)
    return epsilon

def create_ai_players(db):
    """
    Crée ou récupère les joueurs IA dans la base de données.

    Args:
        db: Instance de la base de données utilisée pour la session.

    Returns:
        tuple: Les trois joueurs IA (AI-1, AI-2, Random-AI) sous forme d'objets Player.
    """
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
    """
    Crée une nouvelle instance de jeu avec deux joueurs.

    Args:
        ai1 (Player): Le premier joueur IA.
        ai2 (Player): Le deuxième joueur IA.

    Returns:
        Game: Une nouvelle instance du jeu initialisée avec les deux joueurs.
    """
    new_game = Game(player1_id=ai1.id_player, player2_id=ai2.id_player, table_size=TABLE_SIZE)
    db.session.add(new_game)
    db.session.commit()
    return new_game



def run_game(game, id_random_player):
    """
    Exécute une partie avec les joueurs spécifiés et enregistre les résultats.

    Args:
        game (Game): Instance de jeu à exécuter.
        id_random_player (int): ID du joueur IA aléatoire.

    Returns:
        tuple: Résultats de la partie, incluant :
            - winner (int): ID du gagnant ou 3 en cas de partie bloquée.
            - turn_count (int): Nombre de tours effectués.
            - position (str): Position initiale de l'IA aléatoire ("Top" ou "Bottom").
    """
     
    board = game.boxes

    winner = check_winner(game.boxes)
    turn_count = 0
    print(Fore.YELLOW + f"[INFO] : Lancement de la game id : {game.id_game} ")
    position = "Top" if game.current_player == id_random_player else "Bottom"
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


        adaptedEpsilon = 1 if game.current_player == id_random_player  else epsilon    
        
        possibles_moves = valides_possibles_moves(board, {"x": player_x, "y": player_y, "symbol": symbol})
        move = get_move(game, possibles_moves, adaptedEpsilon, ALPHA, GAMMA, turn_count)
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
        winner = 3 # Si généré, la donnée est aberrante 
    return winner, turn_count, position


def start_training():
    """
    Lance le processus d'entraînement des IA en exécutant des parties successives.

    - Entraîne les IA sur 100 000 parties.
    - Ajuste epsilon à chaque partie pour moduler l'exploration.
    - Effectue des phases de test toutes les 1 000 parties pour évaluer les performances.

    Aucun argument requis.

    Returns:
        None
    """
    nbGames = 0

    finalEpsilon = epsilon
    
    ai1, ai2, randomAi = create_ai_players(db)
    with open("training_phase.csv", "a", newline="") as csvfile:
        fieldnames = ["game_id", "winner_id", "turn_count", "AI_starting_position"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while nbGames < 100000:
            game = create_game(ai1, ai2)
            winner, turn_count, position = run_game(game, randomAi.id_player)
            finalEpsilon = next_epsilon(finalEpsilon)
            nbGames += 1
            
            if nbGames != 0 and nbGames % 10000 == 0:
                print(Fore.RED + "[INFO] : Lancement de la phase de test\n")
                nbTestGames = 0
                while nbTestGames < 100:
                    players = [ai1, randomAi]
                    player1 = random.choice(players)
                    player2 = ai1 if player1 == randomAi else randomAi
                    randomAi = player2 if player2 == randomAi else player1
                    testGame = create_game(player1, player2)
                    winner, turn_count, ai_random_position = run_game(testGame, randomAi.id_player)
                    
                    if winner == 1 and ai_random_position == "Top" or winner == 2 and ai_random_position == "Bottom":
                        winner = 3
                    else:
                        winner = 1
                    writer.writerow({
                        "game_id": testGame.id_game,
                        "winner_id" : winner,
                        "turn_count": turn_count,
                        "AI_starting_position": ai_random_position
                    })

                    nbTestGames += 1
                print(Fore.RED + "[INFO] : Fin de la phase d'entraînement\n")
            


            
        


import time
from collections import deque

from flask import Flask, render_template, request, jsonify, redirect, url_for
from .models import db, Player, Game
from .ai import get_move
from sqlalchemy.exc import SQLAlchemyError
from .viewsFunctions import *



app = Flask(__name__)


app.config.from_object('config')

@app.route('/')
def index():
    return render_template("index.html")
def content(content_id):
    return content_id

@app.route('/loading')
def loading():
    # Simuler un délai de chargement (par exemple 3 secondes)
    time.sleep(1)
    return render_template("loading.html")

@app.route('/game')
def jeu():
    '''
    La fonction "jeu" est responsable de la gestion de la page du jeu, incluant la création des joueurs,
    la création d'une nouvelle instance de jeu et l'envoi des informations pertinentes à la vue.

    Paramètres :
    - Aucun paramètre d'entrée pour cette fonction (utilisation d'un routeur Flask).

    Résultat :
    - Rendu de la vue "game.html" avec les informations du jeu, notamment l'ID du jeu et l'état initial de la grille (grid_state).
    '''
    player1 = Player.query.filter_by(name="Player 1").first()
    player2 = Player.query.filter_by(name="Player IA").first()

    # Si les joueurs n'existent pas, vous pouvez les créer ici.
    if not player1:
        player1 = Player(name="Player 1", is_human=True)
        db.session.add(player1)
        db.session.commit()  
    
    if not player2:
        player2 = Player(name="Player IA", is_human=False)
        db.session.add(player2)
        db.session.commit()

    # Créer une instance de `Game` avec les `id` des deux joueurs
    table_size = 5  # Par exemple, la taille de la table (peut être passée en paramètre)
    new_game = Game(player1_id=player1.id_player, player2_id=player2.id_player, table_size=table_size)
    db.session.add(new_game)
    db.session.commit()

    # Passer `id_game` à la vue pour l'utiliser dans le frontend
    return render_template('game.html', game_id=new_game.id_game, grid_state = new_game.boxes )



@app.route('/travel_request', methods=['POST'])
def travel_request():
    '''
    La fonction "travel_request" est responsable de traiter une requête de déplacement envoyée par le joueur humain ou l'IA,
    et d'effectuer le mouvement approprié en mettant à jour l'état du jeu, en validant le mouvement, et en passant à l'IA si nécessaire.

    Paramètres :
    - Aucune donnée directe, mais la requête POST doit contenir les données suivantes dans le format JSON :
        - current_x : le déplacement horizontal demandé par le joueur humain
        - current_y : le déplacement vertical demandé par le joueur humain
        - game_id : l'ID du jeu actuel pour récupérer l'état du jeu depuis la base de données.

    Résultat :
    - Retourne un JSON contenant :
        - new_grid : la grille mise à jour après les mouvements du joueur humain et de l'IA
        - new_current_player_x, new_current_player_y : les nouvelles positions du joueur courant
        - other_x, other_y : les anciennes positions du joueur précédent
        - winner : le gagnant actuel ou une valeur indiquant l'état de la partie.
    '''
    # partie pour prendre en compte le mouvement du joueur humain
    data = request.json # récupére les données du client 
    movement_x = data.get("current_x")
    movement_y = data.get("current_y")
    game_id = data.get("game_id")

    current_game = Game.query.get(game_id)
    player1_id = current_game.player1_id
    player2_id = current_game.player2_id
    current_player = current_game.current_player
    player_symbol = "1" 
    player_x = current_game.playerpos1_x
    player_y = current_game.playerpos1_y 
    array_string = current_game.boxes
    # résultat du tableau par rapport au mouvement de l'humain
    movement_position = {"x": movement_x, "y": movement_y}
    player_data = {
        "x": player_x,
        "y": player_y,
        "symbol": player_symbol
    }

    result_player1 = is_valid_movement(movement_position, array_string, player_data)
    
    if result_player1 == - 1 :
        return jsonify({
        "new_grid": current_game.boxes,
        "winner": check_winner(current_game.boxes),
        "new_current_player_x": current_game.playerpos1_x,
        "new_current_player_y": current_game.playerpos1_y,
        "other_x": current_game.playerpos2_x,    # ou vice versa si needed
        "other_y": current_game.playerpos2_y
    }), 400  # code HTTP 400 Bad Request, par ex.


    if (current_player == player1_id):
        new_x_player1, new_y_player1, array_string_player1 = result_player1
        # pour enregister les nouvelles positions, et position, et passé la main à l'IA
        last_player_x, last_player_y, new_player_x, new_player_y = current_game.apply_movement(new_x_player1,new_y_player1,array_string_player1)
        
        current_player = player2_id
        db.session.commit()
    # changement appliquer : on donne a l'IA, les differents mouvements possibles, (todo : pour respecter les couches ?)
    possibles_moves = valides_possibles_moves(array_string_player1, {"x" : last_player_x, "y" : last_player_y, "symbol" : "2"})
    # après avoir choisies le mouvement, l'ia apliquer les changements a la base de donnees, elle renvoie le resultat pour l'affichage 
    chosen_move = get_move(current_game, possibles_moves)
    #print("choise move :",chosen_move)
    result_IA = is_valid_movement(chosen_move, array_string_player1, {"x": last_player_x,"y": last_player_y, "symbol" : "2"})

    current_player = player1_id #todo  : utile ? 
    db.session.commit() 

    new_x_IA, new_y_IA, array_string_IA = result_IA
    new_player_x, new_player_y, last_player_x, last_player_y = current_game.apply_movement(new_x_IA,new_y_IA,array_string_IA)
    checkBoard()
    array_string_IA = current_game.boxes #todo : cela sert a quoi deja 
    winner = check_winner(array_string_IA)
    return jsonify({"new_grid" : array_string_IA, "new_current_player_x" : new_player_x, "new_current_player_y" : new_player_y, "other_x": last_player_x, "other_y": last_player_y, "winner" : winner })




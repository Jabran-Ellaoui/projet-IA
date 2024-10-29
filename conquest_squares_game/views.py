from flask import Flask, render_template, request, jsonify 
from .models import db, Player, Game
from .ai import get_move
import requests # todo : peut être inutile 
app = Flask(__name__)

app.config.from_object('config')

@app.route('/')
def index():
    return render_template("index.html")
def content(content_id):
    return content_id
@app.route('/game')
  # Supposons que vous ayez déjà des joueurs dans la base de données.
    # Vous pouvez récupérer les `id_player` des joueurs ou en créer de nouveaux.
def jeu():
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
    db.session.commit()  # Sauvegarde le jeu pour obtenir `id_game`
    #print("id game : ", new_game.id_game)
    #print("id player 1: ", player1.id_player)
    #print("id player 2: ", player2.id_player)

    # Passer `id_game` à la vue pour l'utiliser dans le frontend
    return render_template('game.html', game_id=new_game.id_game, grid_state = new_game.boxes )

# give -1 if the movement is not ok else give the new position of the player and an up to date array_string
def is_valid_movement(movement, array_string, player):
    # Convertit array_string en une grille de caractères
    print("is valid début : array :", array_string)
    lines = array_string.strip().split(' ')
    grid = [list(line) for line in lines]
    n = len(grid)  # Dimension de la grille
    # Calcule la nouvelle position
    
    new_x = player["x"] + movement["x"]
    new_y = player["y"] + movement["y"]
    # Vérifie les limites de la grille et la présence d'un obstacle
    if not (0 <= new_x < n and 0 <= new_y < n):
        return -1  # Mouvement non autorisé
    
    if grid[new_y][new_x] == 'x' or int(grid[new_y][new_x]) == int( player["symbol"]):
        
        # Mouvement autorisé, mise à jour de la grille
        grid[new_y][new_x] = player["symbol"]  # La nouvelle position prend le symbole du joueur
        
        # Reconstruit array_string avec la grille mise à jour
        modified_array_string = ' '.join(''.join(row) for row in grid)
        # Retourne la nouvelle position et la grille mise à jour
        return new_x, new_y, modified_array_string
    else :
        return -1
#version pour jouer avec soit même,  retirer le _NULL du chemin pour le rendre valide, et adapté les autres chemins en conséquence 
@app.route('/travel_request_NULL', methods=['POST'])
def travel_request_NULL():
    data = request.json # récupére les données du client 
    movement_x = data.get("current_x")
    movement_y = data.get("current_y")

    game_id = data.get("game_id")
    current_game = Game.query.get(game_id)

    player_symbol = "1" if current_game.current_player == current_game.player1_id else "2"
    player_x = current_game.playerpos1_x if player_symbol == "1" else current_game.playerpos2_x
    player_y = current_game.playerpos1_y if player_symbol == "1" else current_game.playerpos2_y
    array_string = current_game.boxes

    result = is_valid_movement({"x": movement_x, "y": movement_y},array_string,{"x": player_x, "y":player_y, "symbol": player_symbol})
    
    if result == - 1 :
        return "-1"

    new_x, new_y, array_string = result
    new_player_x, new_player_y, last_player_y, last_player_x = current_game.apply_movement(new_x,new_y,array_string)

    movement = get_move(game_id)

    return jsonify({"new_grid" : array_string, "new_current_player_x" : new_player_x, "new_current_player_y" : new_player_y, "other_x": last_player_x, "other_y": last_player_y })

def check_winner(grid_string):
    """
    Vérifie si la partie est terminée et détermine le gagnant.
    
    Paramètres:
        grid_string (str): Une chaîne représentant l'état de la grille.
        
    Retourne:
        int: 1 si le joueur humain a gagné, 2 si l'IA a gagné, 0 s'il n'y a pas encore de gagnant.
    """
    # Vérifie s'il reste des "x" dans la grille
    if "x" in grid_string:
        return 0  # Le jeu n'est pas encore terminé
    
    # Compte les occurrences de "1" (joueur humain) et "2" (IA) dans la grille
    count_player1 = grid_string.count("1")
    count_player2 = grid_string.count("2")
    
    # Détermine le gagnant en fonction des compteurs
    if count_player1 > count_player2:
        return 1  # Le joueur humain a gagné
    elif count_player2 > count_player1:
        return 2  # L'IA a gagné
    else:
        return 3  # Égalité ou aucun gagnant déterminé (optionnel)

#version pour jouer contre une IA aléatoire 
@app.route('/travel_request', methods=['POST'])
def travel_request():
    # partie pour prendre en compte le mouvement du joueur humain
    data = request.json # récupére les données du client 
    print("  ------------  travel request : partie humain") 
    movement_x = data.get("current_x")
    movement_y = data.get("current_y")

    game_id = data.get("game_id")
    current_game = Game.query.get(game_id)

    player_symbol = "1" 
    player_x = current_game.playerpos1_x
    player_y = current_game.playerpos1_y 
    array_string = current_game.boxes
    # résultat du tableau par rapport au mouvement de l'humain
    result_human = is_valid_movement({"x": movement_x, "y": movement_y},array_string,{"x": player_x, "y":player_y, "symbol": player_symbol})
    
    

    if result_human == - 1 :
        return "-1"

    new_x_human, new_y_human, array_string_human = result_human
    # pour enregister les nouvelles positions, et position, et passé la main à l'IA 
    last_player_x,last_player_y, new_player_x, new_player_y = current_game.apply_movement(new_x_human,new_y_human,array_string_human)
    db.session.commit() 
    
    # partie pour prendre en compte le mouvement de l'IA 

    print (" ------------  travel request : partie IA ")

    result_IA = -1 
    while result_IA == -1 :
        movement = get_move() 
        
        player_symbol_IA = "2"
        player_x_IA = current_game.playerpos2_x
        player_y_IA = current_game.playerpos2_y

        result_IA = is_valid_movement({"x": movement["x"], "y": movement["y"]},array_string_human, {"x": player_x_IA, "y":player_y_IA, "symbol": player_symbol_IA})
  
    db.session.commit() 
    # partie pour renvoyer le résultat au joueur sous la forme d'une modification html/JS

    new_x_IA, new_y_IA, array_string_IA = result_IA
    new_player_x, new_player_y, last_player_x,last_player_y = current_game.apply_movement(new_x_IA,new_y_IA,array_string_IA)

    winner = check_winner(array_string_IA)

    print( "H-x :", new_player_x, "H-y ", new_player_y,"IA-x ", last_player_x,"IA-y ",last_player_y )
    return jsonify({"new_grid" : array_string_IA, "new_current_player_x" : new_player_x, "new_current_player_y" : new_player_y, "other_x": last_player_x, "other_y": last_player_y, "winner" : winner })
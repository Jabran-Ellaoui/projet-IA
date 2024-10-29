from flask import Flask, render_template, request, jsonify 
from .models import db, Player, Game
import requests # puet être inutile 
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
    player2 = Player.query.filter_by(name="Player 2").first()

    # Si les joueurs n'existent pas, vous pouvez les créer ici.
    if not player1:
        player1 = Player(name="Player 1", is_human=True)
        db.session.add(player1)
        db.session.commit()  # Nécessaire pour obtenir l'ID du joueur
    
    if not player2:
        player2 = Player(name="Player 2", is_human=True)
        db.session.add(player2)
        db.session.commit()

    # Créer une instance de `Game` avec les `id` des deux joueurs
    table_size = 5  # Par exemple, la taille de la table (peut être passée en paramètre)
    new_game = Game(player1_id=player1.id_player, player2_id=player2.id_player, table_size=table_size)
    db.session.add(new_game)
    db.session.commit()  # Sauvegarde le jeu pour obtenir `id_game`

    # Passer `id_game` à la vue pour l'utiliser dans le frontend
    return render_template('game.html', game_id=new_game.id_game, grid_state = new_game.boxes )

def is_valid_movement(movement, array_string, player):
    print("is valid movement : point -1 valeur tableau : ", array_string)
    # Convertit array_string en une grille de caractères
    lines = array_string.strip().split(' ')
    grid = [list(line) for line in lines]
    n = len(grid)  # Dimension de la grille
    print("is valid movement : point 0 ")
    print("player old x: ",player["x"],"player old y",player["y"])
    # Calcule la nouvelle position
    print("movement:", movement)
    print("player:", player)
    new_x = player["x"] + movement["x"]
    new_y = player["y"] + movement["y"]
    print("is valid movement : point 1 ")
    # Vérifie les limites de la grille et la présence d'un obstacle
    if not (0 <= new_x < n and 0 <= new_y < n):
        print("is valid movement : limite par les bornes")
        return -1  # Mouvement non autorisé
    
    print("is valid movement : point 2 ",grid[new_x][new_y] == 'x', grid[new_x][new_y])
    print("avant limite par les symboles : valeur grid case objectif",grid[new_x][new_y])
    if grid[new_y][new_x] == 'x' or int(grid[new_y][new_x]) == int( player["symbol"]):
        
        # Mouvement autorisé, mise à jour de la grille
        grid[new_y][new_x] = player["symbol"]  # La nouvelle position prend le symbole du joueur
        print("is valid movement : point 3 ")
        # Reconstruit array_string avec la grille mise à jour
        modified_array_string = ' '.join(''.join(row) for row in grid)
        print(modified_array_string)
        # Retourne la nouvelle position et la grille mise à jour
        return new_x, new_y, modified_array_string
    else :
        print("is valid movement : limite par les symboles")
        return -1

@app.route('/travel_request', methods=['POST'])
def travel_request():
    data = request.json # récupére les données du client 
    print("app.route : travel_request: point 1") 
    movement_x = data.get("current_x")
    movement_y = data.get("current_y")
    game_id = data.get("game_id")
    current_game = Game.query.get(game_id)
    player_symbol = "1" if current_game.current_player == current_game.player1_id else "2"
    player_x = current_game.playerpos1_x if player_symbol == "1" else current_game.playerpos2_x
    player_y = current_game.playerpos1_y if player_symbol == "1" else current_game.playerpos2_y
    array_string = current_game.boxes
    print("app.route : travel_request: point 2")
    result = is_valid_movement({"x": movement_x, "y": movement_y},array_string,{"x": player_x, "y":player_y, "symbol": player_symbol})
    
    if result == - 1 :
        return "-1"
    new_x, new_y, array_string = result
    new_player_x, new_player_y, last_player_y, last_player_x = current_game.apply_movement(new_x,new_y,array_string)
    print("app.route : travel_request: point 3")
    return jsonify({"new_grid" : array_string, "new_current_player_x" : new_player_x, "new_current_player_y" : new_player_y, "other_x": last_player_x, "other_y": last_player_y })
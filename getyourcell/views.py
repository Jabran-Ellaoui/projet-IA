from flask import Flask, render_template, request, jsonify, current_app as app
from .models import db, Game, Player  # Importation correcte des modèles et de la base de données


# Route pour la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Route pour le jeu
@app.route('/game')
def game():
    return render_template('game.html')

# Route pour récupérer l'état actuel du plateau
@app.route('/get_board')
def get_board():
    gameID = Game.query.get(1)  # On récupère un jeu spécifique (id=1 ici, à adapter selon le cas)
    if game is None:
        return jsonify({"error": "Game not found"}), 404

    board = parse_board(game.boxes)  # Transformation de `boxes` en structure de plateau
    return jsonify(board=board)

# Fonction utilitaire pour transformer la chaîne boxes en tableau 5x5
def parse_board(boxes_str):
    table_size = 5  # Taille du plateau 5x5
    board = []
    index = 0
    for _ in range(table_size):
        row = []
        for _ in range(table_size):
            row.append(boxes_str[index])
            index += 1
        board.append(row)
    return board

# Route pour déplacer un joueur
@app.route('/move', methods=['POST'])
def move():
    data = request.json
    game_id = data['game_id']
    player_id = data['player_id']
    new_x = data['new_x']
    new_y = data['new_y']

    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Position actuelle du joueur
    if player_id == game.player1_id:
        current_x, current_y = game.playerpos1_x, game.playerpos1_y
    elif player_id == game.player2_id:
        current_x, current_y = game.playerpos2_x, game.playerpos2_y
    else:
        return jsonify({"error": "Invalid player ID"}), 400

    try:
        # Valider et exécuter le déplacement
        new_x, new_y = move_player(parse_board(game.boxes), player_id, new_x, new_y, current_x, current_y)
        
        # Mettre à jour la base de données avec la nouvelle position
        update_game_in_db(game, player_id, new_x, new_y)
        
        # Renvoyer le plateau mis à jour
        updated_board = parse_board(game.boxes)
        return jsonify(success=True, board=updated_board)

    except ValueError as e:
        return jsonify(success=False, error=str(e))

# Fonction pour valider et effectuer un déplacement
def move_player(board, player_id, new_x, new_y, current_x, current_y):
    # Vérifier que le déplacement est valide (à une case d’écart, case libre, etc.)
    if abs(new_x - current_x) > 1 or abs(new_y - current_y) > 1:
        raise ValueError("Invalid move: out of range")

    if board[new_x][new_y] != "x":
        raise ValueError("Invalid move: cell already occupied")

    return new_x, new_y

# Fonction pour mettre à jour la base de données avec la nouvelle position
def update_game_in_db(game, player_id, new_x, new_y):
    if player_id == game.player1_id:
        game.playerpos1_x = new_x
        game.playerpos1_y = new_y
    elif player_id == game.player2_id:
        game.playerpos2_x = new_x
        game.playerpos2_y = new_y
    
    # Marquer la case comme prise dans la chaîne `boxes`
    table_size = 5
    index = new_x * table_size + new_y
    boxes_list = list(game.boxes)
    boxes_list[index] = str(player_id)  # Marquer la case avec l'ID du joueur
    game.boxes = "".join(boxes_list)
    
    db.session.commit()

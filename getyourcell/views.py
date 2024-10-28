from flask import Flask, render_template, request, jsonify
from . import models

app = Flask(__name__)
app.config.from_object('config')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/get_board')
def get_board():
    game = game.query.get(1)  # Exemple avec une partie spécifique
    board = parse_board(game.boxes)
    return jsonify(board=board)

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    game_id = data['game_id']
    player_id = data['player_id']
    new_x = data['new_x']
    new_y = data['new_y']

    game = game.query.get(game_id)
    board = parse_board(game.boxes)

    # Position actuelle du joueur
    if player_id == 1:
        current_x, current_y = game.player1pos_x, game.player1pos_y
    else:
        current_x, current_y = game.player2pos_x, game.player2pos_y

    try:
        new_x, new_y = move_player(board, player_id, new_x, new_y, current_x, current_y)
        update_game_in_db(game, board, player_id, new_x, new_y)
        return jsonify(success=True, board=board)

    except ValueError as e:
        return jsonify(success=False, error=str(e))
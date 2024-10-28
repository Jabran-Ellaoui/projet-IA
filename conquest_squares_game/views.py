from flask import Flask,render_template,request,jsonify
from .ai import get_move

from flask import Flask, render_template
from . import models
from .models import Player, db, Game

app = Flask(__name__)

app.config.from_object('config')

@app.route('/')
def index():
    return render_template("index.html")
def content(content_id):
    return content_id
@app.route('/game')
def jeu():
    return render_template('game.html')

@app.route("/start_game", methods=['POST'])
def start_game():
    # Example setup for creating or fetching players
    player1 = Player.query.filter_by(name="Player1").first() or Player(name="Player1", is_human=True)
    player2 = Player.query.filter_by(name="Player2").first() or Player(name="Player2", is_human=False)

    # Add players to the session if they don’t exist in the database
    if not player1.id_player:
        db.session.add(player1)
    if not player2.id_player:
        db.session.add(player2)

    db.session.commit()  # Commit to ensure players are saved and have IDs

    # Now initialize the game with player IDs
    new_game = Game(player1_id=player1.id_player, player2_id=player2.id_player,table_size=5)
    db.session.add(new_game)
    db.session.commit()

    print(f"Player 1 ID: {player1.id_player}")
    print(f"Player 2 ID: {player2.id_player}")

    size= 5
    gameState = {
        "board": [["0" for _ in range(size)] for _ in range(size)],  # Use '0' for empty cells
        "posPlayer1": {"x": 0, "y": 0},
        "posPlayer2": {"x": size - 1, "y": size - 1},
        "currentPlayer": 1
    }
    new_game.boxes = "1xxxx xxxxx xxxxx xxxxx xxxx2"


    # Mark initial player positions on the board
    gameState["board"][0][0] = "1"  # Player 1 represented by '1'
    gameState["board"][size - 1][size - 1] = "2"  # Player 2 represented by '2'

    db.session.commit()
    return jsonify({
        "status": "success",
        "gameId": new_game.id_game,
        "gameState": gameState
    })

@app.route('/gameboard', methods=['GET'])
def get_board():
    current_game = db.session.query(Game).first()  # Get the first game record
    if current_game:
        # Assuming current_game.boxes holds the board state as a string
        return jsonify({"board": current_game.boxes})  # Return the board as a JSON object
    else:
        return jsonify({"error": "Game not found"}), 404
@app.route('/validate_move', methods=['POST'])
def validate_move():
    data = request.json
    current_player = data.get('currentPlayer')
    new_position = data.get('newPosition')

    # Example logic to determine if the move is valid
    if not new_position or current_player not in [1, 2]:
        return jsonify({"valid": False, "error": "Invalid data"}), 400

    # Assuming you have a function to check if the move is valid
    # You might need to adjust the logic based on your actual game rules
    is_valid = check_move_validity(current_player, new_position)  # Implement this function based on your game logic

    return jsonify({"valid": is_valid})
def check_move_validity(current_player, new_position):
    pass
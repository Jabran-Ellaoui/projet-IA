from flask import Flask, render_template, request,jsonify
from . import models
from .ai import get_move
from .models import Player, Game, db
import random
import requests

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


@app.route('/start_game', methods=['POST'])
def start_game():
    # Reset game state to initial conditions
    global gameState

    # Ensure your player creation logic is in place.
    # Replace these with your actual player retrieval/creation logic.
    player1 = Player(name='Player 1', is_human=True)  # Example: create or get the first player
    player2 = Player(name='Player 2', is_human=True)  # Example: create or get the second player

    # Add players to the database
    db.session.add(player1)
    db.session.add(player2)
    db.session.commit()  # Commit to save players

    # Create the game instance in the database
    new_game = Game(player1_id=player1.id_player, player2_id=player2.id_player)
    db.session.add(new_game)
    db.session.commit()  # Commit to save the game

    # Initialize game state in memory (optional)
    BOARD_SIZE = 5
    gameState = {
        "board": [["0" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],  # Use '0' for empty cells
        "posPlayer1": {"x": 0, "y": 0},
        "posPlayer2": {"x": BOARD_SIZE - 1, "y": BOARD_SIZE - 1},
        "currentPlayer": 1
    }

    # Mark initial player positions on the board
    gameState["board"][0][0] = "1"  # Player 1 represented by '1'
    gameState["board"][BOARD_SIZE - 1][BOARD_SIZE - 1] = "2"  # Player 2 represented by '2'

    # Update the game instance's boxes representation
    new_game.boxes = "1xxxx xxxxx xxxxx xxxxx xxxx2"  # Example box initialization
    db.session.commit()  # Save the updated game state in the database

    # Return a response with the game ID and initial game state
    return jsonify({
        "status": "success",
        "gameId": new_game.id_game,
        "gameState": gameState
    }), 200




# Fonction pour vérifier si un mouvement est valide
def isMoveValid(playerPos, x, y):
    distance = abs(playerPos["x"] - x) + abs(playerPos["y"] - y)
    return distance == 1 and gameState["board"][x][y] == ""

# Fonction pour trouver les mouvements valides autour d'une position
def getValidMoves(playerPos):
    x, y = playerPos["x"], playerPos["y"]
    possible_moves = [
        (x - 1, y), (x + 1, y),  # Haut et bas
        (x, y - 1), (x, y + 1)   # Gauche et droite
    ]
    return [(nx, ny) for nx, ny in possible_moves if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and isMoveValid(playerPos, nx, ny)]

# Fonction pour le mouvement aléatoire de l'IA
def aiMove():
    validMove = getValidMoves(gameState["posPlayer2"])
    if validMove:
        x, y = random.choice(validMove)
        gameState["board"][gameState["posPlayer2"]["x"]][gameState["posPlayer2"]["y"]] = ""
        gameState["board"][x][y] = "J2"
        gameState["posPlayer2"] = {"x": x, "y": y}

# On doit créer une route qui va venir récupérer le mouvement via la méthode post (DIFFERENT DU GAME qu'on af ait)
@app.route('/play', methods=['POST'])
def play():
    data = request.json
    x = data['x']
    y = data['y']
    player_id = data['player']

    # Retrieve the current game instance (you may need to modify this to get the specific game)
    game = Game.query.first()  # Fetch the first game for simplicity

    # Validate the move
    boxes_list = list(game.boxes.replace(" ", ""))  # Remove spaces for easier manipulation
    index = x * 5 + y  # Calculate the index for the 5x5 grid

    if boxes_list[index] == 'x' and player_id == game.current_player:  # Valid move
        # Update the board
        boxes_list[index] = '1' if player_id == game.player1_id else '2'

        # Update player positions (not shown here, but you'd typically want to move based on game logic)
        if player_id == game.player1_id:
            game.playerpos1_x, game.playerpos1_y = x, y
        else:
            game.playerpos2_x, game.playerpos2_y = x, y

        # Update the current player
        game.current_player = game.player2_id if player_id == game.player1_id else game.player1_id

        # Update the boxes back to string format
        game.boxes = "".join(boxes_list[:5]) + " " + "".join(boxes_list[5:10]) + " " + \
                     "".join(boxes_list[10:15]) + " " + "".join(boxes_list[15:20]) + " " + \
                     "".join(boxes_list[20:25])

        db.session.commit()  # Commit changes to the database

        return jsonify({'gameState': {
            'board': game.boxes.split(" "),  # Send the updated board back to the client
            'currentPlayer': game.current_player
        }})
    else:
        return jsonify({'status': 'invalid_move', 'message': 'Invalid move or cell already occupied.'}), 400

@app.route('/game_state', methods=['GET'])
def get_game_state():
    game = Game.query.first()  # Retrieve the current game (adjust as needed)
    if game is None:
        return jsonify({"error": "Game not found."}), 404  # Handle the case where game is not found
    # Decode the `boxes` string into a 5x5 array
    boxes_grid = []
    for i in range(5):
        row = list(game.boxes[i * 5:(i + 1) * 5])  # Take 5 characters per row
        boxes_grid.append(row)

    game_state = {
        "board": boxes_grid,
        "posPlayer1": {"x": game.playerpos1_x, "y": game.playerpos1_y},
        "posPlayer2": {"x": game.playerpos2_x, "y": game.playerpos2_y},
        "currentPlayer": game.current_player
    }

    return jsonify(game_state), 200
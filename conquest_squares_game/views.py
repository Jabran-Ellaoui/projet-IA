<<<<<<< Updated upstream
from math import trunc
=======
import time
from collections import deque
>>>>>>> Stashed changes

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
    Game.query.delete()
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

<<<<<<< Updated upstream
    size= 5
    gameState = {
        "board": [["0" for _ in range(size)] for _ in range(size)],  # Use '0' for empty cells
        "posPlayer1": {"x": 0, "y": 0},
        "posPlayer2": {"x": size - 1, "y": size - 1},
        "currentPlayer": 1
    }
    new_game.boxes = "1xxxx xxxxx xxxxx xxxxx xxxx2"
=======

def checkBoard():
    data = request.json
    game_id = data.get("game_id")
    current_game = Game.query.get(game_id)
    grid = current_game.boxes

    # Convert the grid string into a 2D list
    board = [list(row) for row in grid.split()]
    rows, cols = len(board), len(board[0])

    def bfs(r, c):
        queue = deque([(r, c)])
        visited = set([(r, c)])
        enclosing_players = set()
        enclosed_region = [(r, c)]
        is_enclosed = True

        while queue:
            x, y = queue.popleft()

            # Explore neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy

                # If out of bounds, mark as not enclosed
                if nx < 0 or nx >= rows or ny < 0 or ny >= cols:
                    is_enclosed = True
                    continue

                cell = board[nx][ny]
                if cell == 'x' and (nx, ny) not in visited:
                    # Add cell to the region and continue exploration
                    visited.add((nx, ny))
                    queue.append((nx, ny))
                    enclosed_region.append((nx, ny))
                elif cell in {'1', '2'}:
                    # Track the surrounding player
                    enclosing_players.add(cell)

        # If region is fully enclosed by one player and no boundary
        if is_enclosed and len(enclosing_players) == 1:
            enclosing_player = enclosing_players.pop()
            # Update all enclosed 'x' cells
            for x, y in enclosed_region:
                board[x][y] = enclosing_player

    # Check all cells in the board
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 'x':
                bfs(i, j)

    # Update the game board back to string format
    updated_grid = ' '.join([''.join(row) for row in board])
    current_game.boxes = updated_grid
    db.session.commit()
    print(board)


    # Update the game board back to string format
    print(board)
    updated_grid = ' '.join([''.join(row) for row in board])
    current_game.boxes = updated_grid
    db.session.commit()
@app.route('/travel_request', methods=['POST'])
def travel_request():
    # partie pour prendre en compte le mouvement du joueur humain
    data = request.json # récupére les données du client 
    movement_x = data.get("current_x")
    movement_y = data.get("current_y")
>>>>>>> Stashed changes


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
def check_move_validity():
    # Get `i` and `j` from query parameters
    data = request.get_json()
    i = data.get('i')
    j = data.get('j')
    is_valid = move_validation(i, j)
    if (is_valid):
        current_game = db.session.query(Game).first()
        if (current_game.current_player == current_game.player1_id):
            current_game.playerpos1_x = i
            current_game.playerpos1_y = j
            current_game.current_player = current_game.player2_id
        else:
            current_game.current_player = current_game.player1_id
            current_game.playerpos2_x = i
            current_game.playerpos2_y = j
        db.session.commit()

<<<<<<< Updated upstream
=======
    result_IA = -1 
    while result_IA == -1 and current_player == player2_id:
        movement = get_move()
        
        player_symbol_IA = "2"
        player_x_IA = current_game.playerpos2_x
        player_y_IA = current_game.playerpos2_y
>>>>>>> Stashed changes

    return jsonify({'valid': is_valid})
def move_validation(i,j):
    current_game = db.session.query(Game).first()
    currPlayer = current_game.current_player
    if (currPlayer == current_game.player1_id):
        playerX= current_game.playerpos1_x
        playerY= current_game.playerpos1_y
    else:
        playerX = current_game.playerpos2_x
        playerY = current_game.playerpos2_y
    diffX = i -playerX
    diffY = j -playerY
    if (abs(diffX) == 1 and diffY == 0):   # Horizontal move
        return checkOtherPlayerCases(i,j)
    elif (diffX == 0 and abs(diffY) == 1): # Vertical move
        return checkOtherPlayerCases(i,j)

    else:
        return False

    checkBoard()
    return jsonify({"new_grid" : array_string_IA, "new_current_player_x" : new_player_x, "new_current_player_y" : new_player_y, "other_x": last_player_x, "other_y": last_player_y, "winner" : winner })



<<<<<<< Updated upstream
def checkOtherPlayerCases(i, j):
    current_game = db.session.query(Game).first()
    currPlayer = str(current_game.current_player)  # Ensure currPlayer is a string for comparison
    boxes = current_game.boxes

    # Split boxes into a list of lists for easier manipulation
    boxes_segments = [list(row) for row in boxes.split()]

    i = i-1
    j = j-1

    # Check if the target cell is occupied by the current player
    print("segment")
    print(boxes_segments[i][j])
    if boxes_segments[i][j] != currPlayer and boxes_segments[i][j] != 'x':
        return False  # The cell is already occupied by the current player

    # Check if the cell is occupied by another player
    for a in range(len(boxes_segments)):
        for b in range(len(boxes_segments[a])):
            if a == i and b == j:
                # Update the board state to reflect the current player's move
                if (currPlayer == str(current_game.player1_id)):
                    boxes_segments[a][b] = '1'
                elif (currPlayer == str(current_game.player2_id)):
                    boxes_segments[a][b] = '2'
                break  # Break the inner loop once we update

    # Convert the list of lists back to the original string format
    updated_boxes = ' '.join(''.join(row) for row in boxes_segments)

    # Update the current_game object with the new board state
    current_game.boxes = updated_boxes

    # Commit the changes to the database
    db.session.commit()

    return True  # The move was valid and the board has been updated
=======
>>>>>>> Stashed changes

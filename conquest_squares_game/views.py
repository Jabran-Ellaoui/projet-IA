import time
from collections import deque

from flask import Flask, render_template, request, jsonify
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

@app.route('/game')
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
    db.session.commit()

    # Passer `id_game` à la vue pour l'utiliser dans le frontend
    return render_template('game.html', game_id=new_game.id_game, grid_state = new_game.boxes )


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
@app.route('/travel_request', methods=['POST'])
def travel_request():
    # partie pour prendre en compte le mouvement du joueur humain
    data = request.json # récupére les données du client 
    movement_x = data.get("current_x")
    movement_y = data.get("current_y")

    game_id = data.get("game_id")
    current_game = Game.query.get(game_id)
    player1_id = current_game.player1_id
    player2_id = current_game.player2_id
    current_player= current_game.current_player

    player_symbol = "1" 
    player_x = current_game.playerpos1_x
    player_y = current_game.playerpos1_y 
    array_string = current_game.boxes
    # résultat du tableau par rapport au mouvement de l'humain
    result_human = is_valid_movement({"x": movement_x, "y": movement_y},array_string,{"x": player_x, "y":player_y, "symbol": player_symbol})

    if result_human == - 1 :
        return "-1"
    if (current_player == player1_id):
        new_x_human, new_y_human, array_string_human = result_human
        # pour enregister les nouvelles positions, et position, et passé la main à l'IA
        last_player_x,last_player_y, new_player_x, new_player_y = current_game.apply_movement(new_x_human,new_y_human,array_string_human)
        current_player = player2_id
        db.session.commit()

    result_IA = -1 
    while result_IA == -1 and current_player == player2_id:
        movement = get_move(game_id)
        
        player_symbol_IA = "2"
        player_x_IA = current_game.playerpos2_x
        player_y_IA = current_game.playerpos2_y

        result_IA = is_valid_movement({"x": movement["x"], "y": movement["y"]},array_string_human, {"x": player_x_IA, "y":player_y_IA, "symbol": player_symbol_IA})
    current_player = player1_id
    db.session.commit() 

    new_x_IA, new_y_IA, array_string_IA = result_IA
    new_player_x, new_player_y, last_player_x,last_player_y = current_game.apply_movement(new_x_IA,new_y_IA,array_string_IA)
    checkBoard()
    array_string_IA = current_game.boxes
    winner = check_winner(array_string_IA)
    return jsonify({"new_grid" : array_string_IA, "new_current_player_x" : new_player_x, "new_current_player_y" : new_player_y, "other_x": last_player_x, "other_y": last_player_y, "winner" : winner })




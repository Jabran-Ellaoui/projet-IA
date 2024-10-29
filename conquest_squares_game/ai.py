from .models import db, Game, Player
import random

# return acceptable move chose by ai (random) (possibility : (0,1) : up, (1,0) : right, (0,-1) : down, (-1,0): left), without change data in the data base
def get_move(game_id):  
    positif_movement_checking = False

    current_game = db.Game.query.get(game_id)
    current_player_x = current_game.playerpos1_x if current_game.current_player == current_game.player1_id else current_game.playerpos2_x
    current_player_y = current_game.playerpos1_y if current_game.current_player == current_game.player1_id else current_game.playerpos2_y
    current_player_symbol = str(1 if current_game.current_player == current_game.player1_id else 2)
    
    lines = (current_game.boxes).strip().split(' ')
    grid = [list(line) for line in lines]

    while (not positif_movement_checking):
        direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        movement_x, movement_y = direction
        movement = {"x" : movement_x, "y" : movement_y}
        positif_movement_checking = is_valid_movement(movement, grid, {"x" : current_player_x,"y" : current_player_y, "symbol" : current_player_symbol})

    return movement

#return boolean to know if the movement is acceptable or not 
def is_valid_movement(movement, array, player): 
    n = len(array)  # have the dimension of the array
  
    new_x = player.x + movement.x
    new_y = player.y + movement.y
            
    # Vérifier les limites de la grille, Vérifier si la case cible est occupée par un adversaire
    return (0 <= new_x < n and 0 <= new_y < n) and array[new_x][new_y] in ('x', player.symbol)
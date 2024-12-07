import random
from sqlalchemy import Null, nullsfirst, false
from .models import QTable, Game
from .viewsFunctions import is_valid_movement,checkBoard
# return acceptable move chose by ai (random) (possibility : (0,1) : up, (1,0) : right, (0,-1) : down, (-1,0): left), without change data in the data base
import random
from .models import QTable, Game, db

def encode_state_board(boxes, player1_x, player1_y, player2_x, player2_y):
    """
    Encodes the current game state (boxes) into state_board format.
    - Replace Player 1's position with 'A'.
    - Replace Player 2's position with 'B'.
    """
    rows = boxes.split(" ")
    encoded_rows = []

    for y, row in enumerate(rows):
        encoded_row = list(row)  # Convert string to list for mutability
        if y == player1_y:
            encoded_row[player1_x] = 'A'  # Mark Player 1's position
        if y == player2_y:
            encoded_row[player2_x] = 'B'  # Mark Player 2's position
        encoded_rows.append("".join(encoded_row))

    # Join rows back into a single string separated by spaces
    return " ".join(encoded_rows)

def calculate_cell_capture_reward(previous_boxes, new_boxes, ai_symbol="2"):
    """
    Calculate the reward based on the number of cells captured by the AI.
    - Uses `checkBoard` to process the new board state.
    """
    previous_ai_cells = previous_boxes.count(ai_symbol)
    new_ai_cells = new_boxes.count(ai_symbol)

    # Reward is proportional to the increase in AI-controlled cells
    reward = new_ai_cells - previous_ai_cells

    # Add a small penalty if no cells were captured
    print(new_boxes)
    print("new ai cells", new_ai_cells)
    print("previous ai cells", previous_ai_cells)
    print("Reward : ", reward)
    return reward if reward > 0 else -1

def reset_esperance (qTable_instance, possibles_moves) : 
    if(possibles_moves[0]) :
        qTable_instance.esperance_haut = 0.0
    if(possibles_moves[1]) :
        qTable_instance.esperance_droit = 0.0
    if (possibles_moves[2]) : 
        qTable_instance.esperance_bas = 0.0
    if(possibles_moves[3]) :
        qTable_instance.esperance_gauche = 0.0

    return qTable_instance
# si on veut creer une instance, il faut savoir les quelles sont nullables
def instance_QTable(state_board, possibles_moves):
    # Fetch or create a Q-table entry for the current state
    qTable_instance = QTable.query.filter_by(state_board = state_board).first()
    if not qTable_instance:
        qTable_instance = QTable(
            state_board = state_board,
            esperance_droit=None,
            esperance_gauche=None,
            esperance_haut=None,
            esperance_bas=None
        )
        qTable_instance = reset_esperance(qTable_instance, possibles_moves)
        db.session.add(qTable_instance)
        db.session.commit()
    return qTable_instance

def exploration (valides_possibles_moves):
    filtered_moves = [move for move in valides_possibles_moves if move is not None]
    return random.choice(filtered_moves)

def exploitation(q_entry, current_game, valides_possibles_moves):
    esperances_moves = [
        (q_entry.esperance_haut, valides_possibles_moves[0]),
        (q_entry.esperance_droit, valides_possibles_moves[1]),
        (q_entry.esperance_bas, valides_possibles_moves[2]),
        (q_entry.esperance_gauche, valides_possibles_moves[3])
    ]
    print(esperances_moves)
    valid_esperances_moves = [(esperance, move) for esperance, move in esperances_moves if esperance is not None and move is not None]

    max_esperance, best_move = max(valid_esperances_moves, key=lambda x: x[0])

    print("fin exploitation : ", best_move)

    return best_move

# todo : il faut l'elimine cette fois ci, elle ne sert que dans le cas ou il y a quelque chose d'utile 
def fonction_a_eliminer (current_game, result, move, q_entry, alpha = 0.9, gamma = 0.2):
    # Apply the valid move
    new_x, new_y, new_boxes = result
    previous_boxes = current_game.boxes
    current_game.boxes = new_boxes
    db.session.commit()  # Ensure the database is updated for checkBoard
    checkBoard()  # Process board captures
    processed_boxes = current_game.boxes
    reward = calculate_cell_capture_reward(previous_boxes, processed_boxes)

    # Update Q-values for all actions
    action_map = {"right": "esperance_droit", "left": "esperance_gauche", "up": "esperance_haut", "down": "esperance_bas"}
    for action, (dx, dy) in zip(["right", "left", "down", "up"], [(1, 0), (-1, 0), (0, -1), (0, 1)]):
        next_result = is_valid_movement({"x": dx, "y": dy}, current_game.boxes, {"x": current_game.playerpos2_x, "y": current_game.playerpos2_y, "symbol": "2"})
        if next_result == -1:
            continue  # Skip invalid moves
        _, _, next_boxes = next_result
        next_state_board = encode_state_board(
            next_boxes,
            current_game.playerpos1_x,
            current_game.playerpos1_y,
            current_game.playerpos2_x + dx,
            current_game.playerpos2_y + dy
        )

        next_q_entry = QTable.query.filter_by(state_board=next_state_board).first()
        max_next_q_value = 0.0
        if next_q_entry:
            max_next_q_value = max(
                next_q_entry.esperance_droit,
                next_q_entry.esperance_gauche,
                next_q_entry.esperance_haut,
                next_q_entry.esperance_bas
            )

        current_q_value = getattr(q_entry, action_map[action])
        updated_q_value = current_q_value + alpha * (reward + gamma * max_next_q_value - current_q_value)
        setattr(q_entry, action_map[action], updated_q_value)

    db.session.commit()
    print(f"Updated Q-value for action {move}: {updated_q_value}")

    print("Espe droitre", q_entry.esperance_droit)
    print("Espe gauche", q_entry.esperance_gauche)
    print("Espe bas", q_entry.esperance_bas)
    print("Espe haut", q_entry.esperance_haut)
    return move



# en fait je pense que cette fonction ne fait que renvoie un mouvement pas besoin de plus d'élément, il seront ajouté plus loin. 
def get_move(current_game, valides_possibles_moves, epsilon=0.1, alpha=0.2, gamma=0.9):
    """
    AI chooses and learns a move using Q-learning logic.
    - Epsilon: Exploration rate.
    - Alpha: Learning rate.
    - Gamma: Discount factor.
    """
   
    # crée ID de l'instance possible de QTable, a partir du plateau actuelle 
    state_board = encode_state_board(
        current_game.boxes,
        current_game.playerpos1_x,
        current_game.playerpos1_y,
        current_game.playerpos2_x,
        current_game.playerpos2_y
    )

    print("Current State Board:", state_board)
    # cree ou recupere une instance de qtable selon sont existance par rapport a un etat donnee d'un plateau 
    q_entry = instance_QTable(state_board, valides_possibles_moves)
    
    # Exploration vs. Exploitation
    if random.random() < epsilon:
        # Exploration: Choose a random move
        chosen_move = exploration(valides_possibles_moves)
    else:
        # Exploitation: Choose the best move based on esperances of an instance of Q-values
        chosen_move = exploitation(q_entry, current_game, valides_possibles_moves) 
        
    #ici qu'on fait l'apprentissage 
  
    return chosen_move



        
       



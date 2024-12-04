import random
from sqlalchemy import nullsfirst, false
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

def get_move(game_id, epsilon=0.1, alpha=0.2, gamma=0.9):
    """
    AI chooses and learns a move using Q-learning logic.
    - Epsilon: Exploration rate.
    - Alpha: Learning rate.
    - Gamma: Discount factor.
    """
    current_game = Game.query.get(game_id)
    if not current_game:
        raise ValueError(f"Game with ID {game_id} not found.")

    # Encode the current state to use as a key in the Q-table
    state_board = encode_state_board(
        current_game.boxes,
        current_game.playerpos1_x,
        current_game.playerpos1_y,
        current_game.playerpos2_x,
        current_game.playerpos2_y
    )
    print("Current State Board:", state_board)

    # Fetch or create a Q-table entry for the current state
    q_entry = QTable.query.filter_by(state_board=state_board).first()
    if not q_entry:
        q_entry = QTable(
            state_board=state_board,
            esperance_droit=0.01,
            esperance_gauche=0.01,
            esperance_haut=0.01,
            esperance_bas=0.01
        )
        db.session.add(q_entry)
        db.session.commit()

    # Exploration vs. Exploitation
    if random.random() < epsilon:
        # Exploration: Choose a random move
        while True:
            move = random.choice([{"x": 1, "y": 0}, {"x": -1, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": -1}])
            result = is_valid_movement(move, current_game.boxes, {"x": current_game.playerpos2_x, "y": current_game.playerpos2_y, "symbol": "2"})
            if result != -1:
                print("Exploration move chosen:", move)
                break
        return move
    else:
        # Exploitation: Choose the best move based on Q-values
        moves = [
            {"move": {"x": 1, "y": 0}, "value": q_entry.esperance_droit},
            {"move": {"x": -1, "y": 0}, "value": q_entry.esperance_gauche},
            {"move": {"x": 0, "y": 1}, "value": q_entry.esperance_bas},
            {"move": {"x": 0, "y": -1}, "value": q_entry.esperance_haut},
        ]
        move = max(moves, key=lambda m: m["value"])["move"]
        print("Best move selected based on Q-values:", move)

        result = is_valid_movement(move, current_game.boxes, {"x": current_game.playerpos2_x, "y": current_game.playerpos2_y, "symbol": "2"})
        if result == -1:
            print("Selected move is invalid, retrying...")
            return get_move(game_id, epsilon, alpha, gamma)

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



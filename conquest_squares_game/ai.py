import random
from sqlalchemy import Null, nullsfirst, false
from .models import QTable, Game
from .viewsFunctions import is_valid_movement,checkBoard

import random
from .models import QTable, Game, History, db
from colorama import Fore, Back, Style, init

init() # Initialisation de Colorama pour le debug

MOVE_TO_ATTR = {
    "up":    "esperance_up",
    "right": "esperance_right",
    "down":  "esperance_down",
    "left":  "esperance_left"
}

def get_max_esperance(q_instance):
    """
    Permet de retourner la valeur d'espérance maximale.

    Prend en paramètre une instance de la Q_Table et renvoie la valeur maximale possible.
    """
    esperanceList = []
    if q_instance.esperance_up is not None:
        esperanceList.append(q_instance.esperance_up)
    if q_instance.esperance_right is not None:
        esperanceList.append(q_instance.esperance_right)
    if q_instance.esperance_left is not None:
        esperanceList.append(q_instance.esperance_left)
    if q_instance.esperance_down is not None:
        esperanceList.append(q_instance.esperance_down)

    if not esperanceList:
        return 0.0
    
    return max(esperanceList)


def encode_state_board(boxes, player1_x, player1_y, player2_x, player2_y):
    """
    Code l'état actuel du jeu sous forme d'une représentation de la grille.

    Cette fonction prend l'état actuel du jeu sous forme de grille (représentée par une chaîne de caractères),
    et l'encode en marquant les positions du Joueur 1 et du Joueur 2 sur le plateau :
    - La position du Joueur 1 est marquée par 'A'.
    - La position du Joueur 2 est marquée par 'B'.

    Paramètres :
    - boxes (str) : Une chaîne représentant l'état actuel du plateau de jeu. Chaque ligne est 
      représentée par une chaîne de caractères, et les lignes sont séparées par des espaces. 
      Le plateau est supposé avoir une taille fixe (par exemple, 5x5, 10x10).
    - player1_x (int) : La coordonnée x (colonne) du Joueur 1 sur le plateau.
    - player1_y (int) : La coordonnée y (ligne) du Joueur 1 sur le plateau.
    - player2_x (int) : La coordonnée x (colonne) du Joueur 2 sur le plateau.
    - player2_y (int) : La coordonnée y (ligne) du Joueur 2 sur le plateau.

    Retourne :
    - str : Une nouvelle chaîne représentant le plateau avec la position du Joueur 1 marquée par 'A' 
      et la position du Joueur 2 marquée par 'B'.
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

def calculate_cell_capture_reward(previous_boxes, new_boxes, ai_symbol):
    """
    Calcule la récompense basée sur le nombre de cases capturées par l'IA.

    Cette fonction calcule la récompense en fonction du nombre de cases contrôlées par l'IA 
    avant et après un mouvement. Elle mesure l'augmentation des cases contrôlées par l'IA 
    en comparant l'état du plateau avant et après le mouvement.

    Paramètres :
    - previous_boxes (str) : L'état du plateau avant le mouvement, représenté par une chaîne de caractères. 
      Chaque case est représentée par un caractère, et l'IA est représentée par `ai_symbol`.
    - new_boxes (str) : L'état du plateau après le mouvement, également représenté par une chaîne de caractères.
    - ai_symbol (str, optionnel) : Le symbole utilisé pour représenter l'IA sur le plateau. Par défaut, il s'agit de "2".

    Retourne :
    - int : La récompense calculée en fonction de l'augmentation des cases contrôlées par l'IA. 
      Si aucune case n'a été capturée, une petite pénalité est appliquée, retournant -1. 
      Si des cases ont été capturées, la récompense correspond à l'augmentation du nombre de cases contrôlées.
    """
    previous_ai_cells = previous_boxes.count(ai_symbol)
    new_ai_cells = new_boxes.count(ai_symbol)

    # penalty depending on the opponent
    previous_other_player_cells = sum(1 for symbol in previous_boxes if symbol not in [' ', 'x', ai_symbol])
    new_other_player_cells = sum(1 for symbol in new_boxes if symbol not in [' ', 'x', ai_symbol])

    # Reward is proportional to the increase in AI-controlled cells
    reward = (new_ai_cells - previous_ai_cells if new_ai_cells - previous_ai_cells > 0 else -1) - 0.5 * (new_other_player_cells - previous_other_player_cells)
    
    if 'x' not in new_boxes :
        if new_ai_cells > new_other_player_cells : 
            reward += 10
        else :
            reward -= 10

    # Add a small penalty if no cells were captured
    #print(new_boxes)
    #print("new ai cells", new_ai_cells)
    #print("previous ai cells", previous_ai_cells)
    #print("Reward : ", reward)
    return reward 


# si on veut creer une instance, il faut savoir les quelles sont nullables
def instance_QTable(state_board):
    """
    Récupère ou crée une entrée dans la table Q pour l'état actuel du jeu.

    Cette fonction cherche dans la base de données une entrée de Q-table correspondant à l'état actuel du jeu (state_board).
    Si aucune entrée n'est trouvée, elle crée une nouvelle entrée avec des valeurs d'espérance initialisées à 0,
    puis les réinitialise en fonction des mouvements possibles fournis.

    Paramètres :
    - state_board (str) : La représentation de l'état actuel du plateau de jeu, sous forme de chaîne de caractères.

    Retourne :
    - QTable : L'instance de la table Q correspondant à l'état du jeu. Si elle n'existait pas, elle a été créée et 
      ajoutée à la base de données.
    """
    # Fetch or create a Q-table entry for the current state
    qTable_instance = QTable.query.filter_by(state_board = state_board).first()
    if not qTable_instance:
        qTable_instance = QTable(
            state_board = state_board,
            esperance_right=0.0,
            esperance_left=0.0,
            esperance_up=0.0,
            esperance_down=0.0
        )
        db.session.add(qTable_instance)
        db.session.commit()
    return qTable_instance

def exploration (possibles_moves):
    """
    Effectue une exploration en choisissant aléatoirement un mouvement valide parmi les mouvements possibles.

    Cette fonction filtre les mouvements valides (qui ne sont pas None) dans la liste des mouvements possibles,
    puis choisit aléatoirement l'un de ces mouvements pour explorer de nouvelles options. Cela fait partie de la 
    stratégie d'exploration dans un algorithme d'apprentissage par renforcement (comme le Q-learning).

    Paramètres :
    - possibles_moves (list) : Une liste des mouvements possibles sous la forme d'un string ("right","left","up","down")

    Retourne :
    - Le mouvement choisi aléatoirement parmi les mouvements valides toujours sous la forme d'un string. 
    """
    return random.choice(possibles_moves)

def exploitation(q_entry, possibles_moves):
    """
    Effectue une exploitation en choisissant le mouvement avec la plus grande espérance parmi les mouvements possibles.

    Cette fonction sélectionne le mouvement qui a la plus grande valeur d'espérance parmi les mouvements valides. 
    Elle utilise les valeurs d'espérance stockées dans l'instance `q_entry` (qui représente une entrée de la table Q) 
    pour évaluer chaque mouvement possible, puis choisit celui qui maximise cette espérance.

    Paramètres :
    - q_entry (QTable) : Une instance de la table Q qui contient les valeurs d'espérance pour chaque direction de mouvement 
      (haut, droite, bas, gauche).
    - possibles_moves (list) : Une liste des mouvements possibles, où chaque élément correspond à un mouvement valide 
      (par exemple, "haut", "bas", "gauche", "droite").

    Retourne :
    - string : le mouvement avec l'espérance la plus grande.
    """
    esperances_moves = {
        "up": q_entry.esperance_up,
        "right": q_entry.esperance_right,
        "down": q_entry.esperance_down,
        "left": q_entry.esperance_left
    }
    
    # Filtrer pour ne garder que les mouvements valides
    valid_esperances = {move: esperances_moves[move] for move in possibles_moves}

    # Trouver le mouvement avec la valeur d'espérance maximale
    best_move = max(valid_esperances, key=valid_esperances.get)
    
    return best_move


# en fait je pense que cette fonction ne fait que renvoie un mouvement pas besoin de plus d'�l�ment, il seront ajout� plus loin. 
def get_move(current_game, possibles_moves, epsilon=0.1, alpha=0.2, gamma=0.9):
    """
    L'IA choisit et apprend un mouvement en utilisant la logique du Q-learning.

    Cette fonction permet à l'IA de choisir un mouvement en fonction de l'exploration et de l'exploitation, selon 
    l'algorithme de Q-learning. L'IA choisit un mouvement aléatoire (exploration) avec un certain taux de probabilité 
    (epsilon) ou sélectionne le meilleur mouvement basé sur les valeurs d'espérance actuelles (exploitation).

    Paramètres :
    - current_game (Game) : L'instance actuelle du jeu qui contient les informations sur l'état du plateau et 
      les positions des joueurs.
    - possibles_moves (list of string) : Liste des mouvements possibles (par exemple, mouvement vers le haut, bas, gauche, droite).
    - epsilon (float, optionnel) : Le taux d'exploration. Définit la probabilité que l'IA choisisse un mouvement aléatoire.
      Par défaut, c'est 0.1.
    - alpha (float, optionnel) : Le taux d'apprentissage. Définit à quel point l'IA met à jour ses valeurs d'espérance. Par défaut, c'est 0.2.
    - gamma (float, optionnel) : Le facteur de discount. Définit l'importance des récompenses futures. Par défaut, c'est 0.9.

    Retourne :
    - dict : le mouvement choisie sous la forme d'un string

    Cette fonction applique également l'apprentissage par renforcement (Q-learning) pour mettre à jour les valeurs d'espérance 
    (Q-values) après chaque mouvement.
    """
    # cr�e ID de l'instance possible de QTable, a partir du plateau actuelle 
    state_board = encode_state_board(
    current_game.boxes,
    current_game.playerpos1_x,
    current_game.playerpos1_y,
    current_game.playerpos2_x,
    current_game.playerpos2_y
    )

    #print("Current State Board:", state_board)
    # cree ou recupere une instance de qtable selon sont existance par rapport a un etat donnee d'un plateau 
    q_entry = instance_QTable(state_board)
    
    # Exploration vs. Exploitation
    if random.random() < epsilon:
        # Exploration: Choose a random move
        chosen_move = exploration(possibles_moves)
        print(Fore.GREEN + "[INFO] : L'IA a choisi l'exploration")
    else:
        # Exploitation: Choose the best move based on esperances of an instance of Q-values
        chosen_move = exploitation(q_entry, possibles_moves)
        print(Fore.GREEN + "[INFO] : L'IA a choisi l'exploitation")
        
    # ici string_move : est bien sous sa forme voulue, un string
    learning_by_renforcing(current_game.current_player,current_game.id_game, q_entry, chosen_move, epsilon, alpha, gamma )

    return chosen_move

def learning_by_renforcing (player_id, game_id, current_qTable_instance, move, epsilon, alpha, gamma):
    """
    Applique l'apprentissage par renforcement pour mettre à jour les valeurs d'espérance de l'IA.

    Cette fonction met à jour les valeurs d'espérance (Q-values) de l'IA en fonction du mouvement effectué et de la récompense obtenue.
    Elle utilise l'algorithme de Q-learning pour ajuster les valeurs d'espérance selon la récompense obtenue et les mouvements précédents.

    Paramètres :
    - player_id (int) : L'identifiant du joueur effectuant le mouvement (IA ou humain).
    - game_id (int) : L'identifiant de la partie en cours.
    - current_qTable_instance (QTable) : L'instance de la table Q pour l'état actuel du plateau, contenant les valeurs d'espérance.
    - move (str) : Le mouvement effectué par l'IA choisie par exploration ou exploitation (par exemple, "up", "down", "left", "right").
    - epsilon (float) : Le taux d'exploration (non utilisé directement dans cette fonction, mais lié à la stratégie d'apprentissage).
    - alpha (float) : Le taux d'apprentissage, qui détermine dans quelle mesure les nouvelles informations influencent les valeurs d'espérance.
    - gamma (float) : Le facteur de discount, qui détermine l'importance des récompenses futures dans l'apprentissage.

    Retourne :
    - None : Cette fonction ne retourne rien, mais met à jour les valeurs d'espérance dans la base de données.

    Fonctionnement :
    - Si aucune entrée d'historique n'existe pour la combinaison `game_id` et `player_id`, une nouvelle entrée est créée dans la table `History`.
    - La fonction calcule ensuite la récompense en fonction du changement de l'état du plateau.
    - Les Q-values (espérances) sont mises à jour pour le mouvement effectué selon la formule de Q-learning.
    - Enfin, l'historique du mouvement et de l'état du plateau est mis à jour dans la base de données.
    """
    game_history = History.query.get((game_id, player_id))
    if not game_history :
        game_history = History (
            id_game = game_id,
            id_player = player_id,
            precedent_state_board =  current_qTable_instance.state_board,   
            precedent_move = move
        )
        db.session.add(game_history)
        print(Fore.GREEN + f"[INFO] : Premier mouvement effectué : {move}")
    else : 
        reward = calculate_cell_capture_reward(game_history.precedent_state_board, current_qTable_instance.state_board, ai_symbol="2")

        previous_move = game_history.precedent_move
        previoux_instance_QTable = QTable.query.get(game_history.precedent_state_board)
        print(Fore.CYAN + f"[INFO] : Mouvement précédent = {previous_move}\n[INFO] : Mouvement actuel = {move}\n[INFO] : Récompense = {reward}\n")
        max_future_value = get_max_esperance(current_qTable_instance)
        print(Fore.CYAN + f"[INFO] : Meilleure valeur estimée pour l'état futur -> {max_future_value}")

        old_attr_name = MOVE_TO_ATTR[previous_move]
        old_value = getattr(previoux_instance_QTable, old_attr_name)
        if old_value is None:
            old_value = 0.0
        
        new_value = old_value + alpha * (reward + gamma * max_future_value - old_value)
        print(Fore.CYAN + f"[INFO] : Mise à jour des valeurs d'espérance")
        print(Fore.CYAN + f"[INFO] : Ancienne valeur -> {old_value}\n[INFO] : Nouvelle valeur -> {new_value}\n")
        setattr(previoux_instance_QTable, old_attr_name, new_value)

        if previous_move == "up":
            previoux_instance_QTable.esperance_up = new_value
        if previous_move == "right":
            previoux_instance_QTable.esperance_right = new_value
        if previous_move == "down":
            previoux_instance_QTable.esperance_down = new_value
        if previous_move == "left":
            previoux_instance_QTable.esperance_left = new_value

        game_history.precedent_state_board = current_qTable_instance.state_board
        game_history.precedent_move = move
    
    db.session.commit()


    



        
       



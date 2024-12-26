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

def calculate_cell_capture_reward(previous_boxes, new_boxes, ai_symbol="2"):
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

    # Reward is proportional to the increase in AI-controlled cells
    reward = new_ai_cells - previous_ai_cells

    # Add a small penalty if no cells were captured
    #print(new_boxes)
    #print("new ai cells", new_ai_cells)
    #print("previous ai cells", previous_ai_cells)
    #print("Reward : ", reward)
    return reward if reward > 0 else -1

def reset_esperance (qTable_instance, possibles_moves) :
    """
    Réinitialise les valeurs d'espérance des mouvements possibles dans une instance de QTable.

    Cette fonction met à zéro les valeurs d'espérance pour les mouvements possibles de l'IA (haut, bas, gauche, droite)
    dans l'instance de QTable, en fonction de la liste des mouvements possibles fournie.

    Paramètres :
    - qTable_instance (QTable) : Une instance de la classe `QTable` qui contient les valeurs d'espérance pour chaque mouvement.
    - possibles_moves (list) : Une liste de booleans représentant les mouvements possibles. 
      Chaque élément de la liste indique si le mouvement correspondant (haut, droite, bas, gauche) est possible :
      - possibles_moves[0] : Mouvement vers le haut
      - possibles_moves[1] : Mouvement vers la droite
      - possibles_moves[2] : Mouvement vers le bas
      - possibles_moves[3] : Mouvement vers la gauche

    Retourne :
    - QTable : L'instance de `QTable` avec les valeurs d'espérance réinitialisées pour les mouvements possibles.
    """ 
    if(possibles_moves[0]) :
        qTable_instance.esperance_up = 0.0
    if(possibles_moves[1]) :
        qTable_instance.esperance_right = 0.0
    if (possibles_moves[2]) : 
        qTable_instance.esperance_down = 0.0
    if(possibles_moves[3]) :
        qTable_instance.esperance_left = 0.0

    return qTable_instance
# si on veut creer une instance, il faut savoir les quelles sont nullables
def instance_QTable(state_board, possibles_moves):
    """
    Récupère ou crée une entrée dans la table Q pour l'état actuel du jeu.

    Cette fonction cherche dans la base de données une entrée de Q-table correspondant à l'état actuel du jeu (state_board).
    Si aucune entrée n'est trouvée, elle crée une nouvelle entrée avec des valeurs d'espérance initialisées à 0,
    puis les réinitialise en fonction des mouvements possibles fournis.

    Paramètres :
    - state_board (str) : La représentation de l'état actuel du plateau de jeu, sous forme de chaîne de caractères.
    - possibles_moves (list) : Une liste représentant les mouvements possibles. Chaque élément est un booléen indiquant 
      si un mouvement dans une direction (haut, bas, gauche, droite) est valide.

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

def exploration (valides_possibles_moves):
    """
    Effectue une exploration en choisissant aléatoirement un mouvement valide parmi les mouvements possibles.

    Cette fonction filtre les mouvements valides (qui ne sont pas None) dans la liste des mouvements possibles,
    puis choisit aléatoirement l'un de ces mouvements pour explorer de nouvelles options. Cela fait partie de la 
    stratégie d'exploration dans un algorithme d'apprentissage par renforcement (comme le Q-learning).

    Paramètres :
    - valides_possibles_moves (list) : Une liste des mouvements possibles, où chaque mouvement peut être une
      direction valide (par exemple, "haut", "bas", "gauche", "droite") ou `None` si le mouvement n'est pas possible.

    Retourne :
    - Le mouvement choisi aléatoirement parmi les mouvements valides. Ce mouvement peut être sous forme de tuple ou 
      toute autre structure définie selon votre implémentation des mouvements.
    """
    filtered_moves = [move for move in valides_possibles_moves if move is not None]
    return random.choice(filtered_moves)

def exploitation(q_entry, valides_possibles_moves):
    """
    Effectue une exploitation en choisissant le mouvement avec la plus grande espérance parmi les mouvements possibles.

    Cette fonction sélectionne le mouvement qui a la plus grande valeur d'espérance parmi les mouvements valides. 
    Elle utilise les valeurs d'espérance stockées dans l'instance `q_entry` (qui représente une entrée de la table Q) 
    pour évaluer chaque mouvement possible, puis choisit celui qui maximise cette espérance.

    Paramètres :
    - q_entry (QTable) : Une instance de la table Q qui contient les valeurs d'espérance pour chaque direction de mouvement 
      (haut, droite, bas, gauche).
    - valides_possibles_moves (list) : Une liste des mouvements possibles, où chaque élément correspond à un mouvement valide 
      (par exemple, "haut", "bas", "gauche", "droite") ou `None` si un mouvement n'est pas valide.

    Retourne :
    - tuple : Le mouvement choisi, représenté par un tuple contenant l'espérance et le mouvement associé. 
      Le mouvement choisi est celui avec l'espérance maximale parmi les mouvements valides.
    """
    esperances_moves = [
        (q_entry.esperance_up, valides_possibles_moves[0]),
        (q_entry.esperance_right, valides_possibles_moves[1]),
        (q_entry.esperance_down, valides_possibles_moves[2]),
        (q_entry.esperance_left, valides_possibles_moves[3])
    ]
    valid_esperances_moves = [(esperance, move) for esperance, move in esperances_moves if esperance is not None and move is not None]

    max_esperance, best_move = max(valid_esperances_moves, key=lambda x: x[0])



    return best_move


# en fait je pense que cette fonction ne fait que renvoie un mouvement pas besoin de plus d'�l�ment, il seront ajout� plus loin. 
def get_move(current_game, valides_possibles_moves, epsilon=0.1, alpha=0.2, gamma=0.9):
    """
    L'IA choisit et apprend un mouvement en utilisant la logique du Q-learning.

    Cette fonction permet à l'IA de choisir un mouvement en fonction de l'exploration et de l'exploitation, selon 
    l'algorithme de Q-learning. L'IA choisit un mouvement aléatoire (exploration) avec un certain taux de probabilité 
    (epsilon) ou sélectionne le meilleur mouvement basé sur les valeurs d'espérance actuelles (exploitation).

    Paramètres :
    - current_game (Game) : L'instance actuelle du jeu qui contient les informations sur l'état du plateau et 
      les positions des joueurs.
    - valides_possibles_moves (list) : Liste des mouvements possibles (par exemple, mouvement vers le haut, bas, gauche, droite).
    - epsilon (float, optionnel) : Le taux d'exploration. Définit la probabilité que l'IA choisisse un mouvement aléatoire.
      Par défaut, c'est 0.1.
    - alpha (float, optionnel) : Le taux d'apprentissage. Définit à quel point l'IA met à jour ses valeurs d'espérance. Par défaut, c'est 0.2.
    - gamma (float, optionnel) : Le facteur de discount. Définit l'importance des récompenses futures. Par défaut, c'est 0.9.

    Retourne :
    - dict : Le mouvement choisi sous forme d'un dictionnaire contenant les coordonnées x et y du mouvement sélectionné.

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
    q_entry = instance_QTable(state_board, valides_possibles_moves)
    
    # Exploration vs. Exploitation
    if random.random() < epsilon:
        # Exploration: Choose a random move
        chosen_move = exploration(valides_possibles_moves)
        print(Fore.GREEN + "[INFO] : L'IA a choisi l'exploration")
    else:
        # Exploitation: Choose the best move based on esperances of an instance of Q-values
        chosen_move = exploitation(q_entry, valides_possibles_moves)
        print(Fore.GREEN + "[INFO] : L'IA a choisi l'exploitation")
        
    movement_tuple = (chosen_move["x"],chosen_move["y"])
    match(movement_tuple):
        case (0,-1):
            string_move = "up"
        case (1,0):
            string_move = "right"
        case (0,1):
            string_move = "down"
        case (-1,0):
            string_move = "left" 


    learning_by_renforcing(current_game.current_player,current_game.id_game, q_entry, string_move, epsilon, alpha, gamma )

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
    - move (str) : Le mouvement effectué par l'IA (par exemple, "up", "down", "left", "right").
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


    



        
       



from flask import Flask, render_template, request, jsonify 
from .models import db, Player, Game
from collections import deque

#un string pour chaque mouvement possible
DIRECTION_MAP = {
        (0, -1): "up",
        (1, 0): "right",
        (0, 1): "down",
        (-1, 0): "left"
    }

#Description des paramètres
def apply_movement(movement, array_string, player):
    '''
    La fonction apply_movement prend en paramètre :

    - movement : Dictionnaire indiquant le déplacement du joueur ({"x": ..., "y": ...}), 
    où "x" et "y" représentent le décalage horizontal et vertical respectivement. 
    Par exemple, {"x": 1, "y": 0} pour un déplacement à droite.
    - array_string : Chaîne représentant l’état actuel de la grille, où chaque ligne est séparée par un espace.
    Les cases sont codées par des caractères (ex :'x' pour une case libre, ou un chiffre pour le symbole d'un joueur).
    - player : Dictionnaire indiquant la position actuelle et le symbole du joueur ({"x": ..., "y": ..., "symbol": ...}).

    La fonction vérifie si le mouvement du joueur est valide sur la grille,
    en s'assurant que le déplacement est dans les limites de la grille 
    et que la case n'est pas déjà occupée par un autre joueur. Si le mouvement est valide, 
    elle met à jour la grille et retourne la nouvelle position du joueur ainsi que la grille mise à jour.
    Sinon, elle retourne -1.

    Résultat : 
    - Si le mouvement est valide, la fonction retourne une tuple (nouvelle position x, nouvelle position y, nouvelle grille).
    - Si le mouvement est invalide, elle retourne -1.
    '''
    # Convertit array_string en une grille de caractères
    lines = array_string.strip().split(' ')
    grid = [list(line) for line in lines]
    n = len(grid)  # Dimension de la grille

    # Calcule la nouvelle position
    new_x = player["x"] + movement["x"]
    new_y = player["y"] + movement["y"]

    # Vérifie les limites de la grille
    if not (0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid)):
        #print(f"Le mouvement {movement} est en dehors des limites: new_x={new_x}, new_y={new_y}")
        return -1  # Mouvement non autorisé

    # Vérifie si la case cible est occupée
    target_cell = grid[new_y][new_x]
    #print(f"Cellule ciblée : {movement}: {target_cell}")

    if target_cell == 'x' or int(target_cell) == int(player["symbol"]):
        # Mouvement autorisé, mise à jour de la grille
        grid[new_y][new_x] = player["symbol"]  # La nouvelle position prend le symbole du joueur
        
        # Reconstruit array_string avec la grille mise à jour
        modified_array_string = ' '.join(''.join(row) for row in grid)
        # Retourne la nouvelle position et la grille mise à jour
        return new_x, new_y, modified_array_string
    else:
        #print(f"Le mouvement {movement} est invalide: la cellule est occupée par {target_cell}")
        return -1
  
#renvoie les mouvements valides sous la forme d'un x et d'un y
def valides_possibles_moves(array_string, player) :
    """
    Retourne une liste de mouvements valides et leurs conséquences sur l'état du jeu.

    Cette fonction teste les mouvements possibles pour un joueur en fonction de l'état actuel du plateau (array_string) et de la position du joueur.
    Elle retourne une liste de mouvements valides où chaque mouvement est accompagné de deux éléments :
    - Le premier élément contient trois attributs : 
        - `new_x` : la nouvelle position horizontale du joueur après le mouvement.
        - `new_y` : la nouvelle position verticale du joueur après le mouvement.
        - `string_array` : le nouvel état du plateau après le mouvement.
    - Le deuxième élément contient deux attributs : 
        - `x` : la coordonnée horizontale du mouvement.
        - `y` : la coordonnée verticale du mouvement.

    Paramètres :
    - array_string (str) : La représentation de l'état actuel du plateau sous forme de chaîne de caractères, où chaque case est représentée par un caractère.
    - player (dict) : Un dictionnaire contenant les informations du joueur (comme les coordonnées de sa position actuelle et son symbole).

    Retourne :
    - list : Une liste de mouvements valides et leurs conséquences. Chaque élément est soit un dictionnaire avec les attributs `x`, `y`, 
    . Les mouvements sont testés selon les coordonnées possibles : haut, droite, bas, gauche.
    """
    valid_moves_and_cons = []
    possibles_moves = [{"x": 0, "y" : -1},{"x": 1, "y" : 0},{"x": 0, "y" : 1},{"x": -1, "y" : 0}]
    for tested_move in possibles_moves :
        result_move = apply_movement(tested_move, array_string, player)
        if result_move != -1 : 
            
            valid_moves_and_cons.append(DIRECTION_MAP[tested_move["x"],tested_move["y"]])       

    return valid_moves_and_cons 
    

def check_winner(grid_string):
    '''
    La fonction check_winner prend en paramètre :

    - grid_string : une chaîne de caractères représentant l'état actuel de la grille,
    où chaque case est un caractère ("x" pour un case libre, "1" pour le joueur 1, "2" pour le joueur 2).

    La fonction vérifie d'abord si des cases libres ("x") sont encore présents dans la grille. Si c'est le cas,
    le jeu n'est pas encore terminé. Sinon, elle compte les occurrences des symboles "1" (joueur humain) et "2" (IA) pour déterminer qui a gagné ou s'il y a égalité.

    Résultat :
    - 0 si le jeu n'est pas encore terminé (présence de case libre).
    - 1 si le joueur humain ("1") a plus de symboles que l'IA.
    - 2 si l'IA ("2") a plus de symboles que le joueur humain.
    - 3 si c'est une égalité.
    '''
    # Vérifie s'il reste des "x" dans la grille
    if "x" in grid_string:
         return 0  # Le jeu n'est pas encore terminé
        
        # Compte les occurrences de "1" (joueur humain) et "2" (IA) dans la grille
    count_player1 = grid_string.count("1")
    count_player2 = grid_string.count("2")
        
    # Détermine le gagnant en fonction des compteurs
    if count_player1 > count_player2:
        return 1  # Le joueur humain a gagné
    elif count_player2 > count_player1:
         return 2  # L'IA a gagné
    else:
         return 3  # Égalité ou aucun gagnant déterminé (optionnel)


def bfs(initial_x, initial_y, totalRows, totalColumns, board):
    """
    Explore une région contiguë sur un tableau en effectuant une recherche en largeur (BFS) 
    pour identifier une zone potentiellement "enfermée" par un joueur.

    Cette fonction vérifie si une région définie par des cellules adjacentes marquées 'x' 
    est entièrement entourée par des bordures ou des cellules appartenant à un joueur ('1' ou '2').
    Si une région est complètement enfermée par un joueur unique, elle est "capturée" et ses 
    cellules sont marquées par le symbole de ce joueur dans le tableau.

    Parameters:
        initial_x (int): Coordonnée de ligne de départ pour l'exploration.
        initial_y (int): Coordonnée de colonne de départ pour l'exploration.
        totalRows (int): Nombre total de lignes dans le tableau.
        totalColumns (int): Nombre total de colonnes dans le tableau.
        board (list[list[str]]): Tableau représentant la grille de jeu. Les cellules peuvent contenir :
            - 'x' : une cellule non capturée.
            - '1', '2' : une cellule appartenant au joueur 1 ou 2.
    
    Returns:
        None: Modifie directement le tableau `board` si une région est capturée.
        
    """
    cell_to_explore = deque([(initial_x, initial_y)])
    visited_cell = set([(initial_x, initial_y)])
    enclosing_players = set()
    enclosed_region = [(initial_x, initial_y)]
    is_enclosed = True

    while cell_to_explore:
        current_x, current_y = cell_to_explore.popleft()

        for x_alteration, y_alteration in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = current_x + x_alteration, current_y + y_alteration

            if new_x < 0 or new_x >= totalRows or new_y < 0 or new_y >= totalColumns:
                is_enclosed = True
                continue

            cell = board[new_x][new_y]
            if cell == 'x' and (new_x, new_y) not in visited_cell:
                visited_cell.add((new_x, new_y))
                cell_to_explore.append((new_x, new_y))
                enclosed_region.append((new_x, new_y))
            elif cell in {'1', '2'}:
                enclosing_players.add(cell)

    if is_enclosed and len(enclosing_players) == 1:
        enclosing_player = enclosing_players.pop()

        for current_x, current_y in enclosed_region:
            board[current_x][current_y] = enclosing_player


def checkBoard():
    '''
    La fonction checkBoard ne prend pas de paramètres :

    - Aucun paramètre direct n'est passé, car elle récupère les données de la requête HTTP via request.json.
    - La fonction utilise game_id pour récupérer l'état actuel du jeu et la grille associée dans la base de données.

    La fonction analyse la grille du jeu, effectue une exploration en largeur (BFS) pour vérifier si des régions sont complètement encerclées par un joueur.
    Si une région est encerclée, elle est remplie avec le symbole du joueur qui a entouré cette région. La grille mise à jour est ensuite enregistrée dans la base de données.

    Résultat :
    - Aucun résultat renvoyé directement, la grille du jeu est mise à jour dans la base de données.
    '''
    data = request.json
    game_id = data.get("game_id")
    current_game = Game.query.get(game_id)
    grid = current_game.boxes

    # Convert the grid string into a 2D list
    board = [list(row) for row in grid.split()]
    rows, cols = len(board), len(board[0])


    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 'x':
                bfs(i, j, rows, cols, board)

    updated_grid = ' '.join([''.join(row) for row in board])
    current_game.boxes = updated_grid
    db.session.commit()

def checkBoardAI(AIboard):
    '''
    La fonction checkBoard ne prend pas de paramètres :

    - Aucun paramètre direct n'est passé, car elle récupère les données de la requête HTTP via request.json.
    - La fonction utilise game_id pour récupérer l'état actuel du jeu et la grille associée dans la base de données.

    La fonction analyse la grille du jeu, effectue une exploration en largeur (BFS) pour vérifier si des régions sont complètement encerclées par un joueur.
    Si une région est encerclée, elle est remplie avec le symbole du joueur qui a entouré cette région. La grille mise à jour est ensuite enregistrée dans la base de données.

    Résultat :
    - Aucun résultat renvoyé directement, la grille du jeu est mise à jour dans la base de données.
    '''
    grid = AIboard

    # Convert the grid string into a 2D list
    board = [list(row) for row in grid.split()]
    rows, cols = len(board), len(board[0])

    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 'x':
                bfs(i, j, rows, cols, board)

    updated_grid = ' '.join([''.join(row) for row in board])
    return updated_grid

def get_player_id(current_game):
    if (current_game.current_player == current_game.player1_id):
        return 1
    else:
        return 2

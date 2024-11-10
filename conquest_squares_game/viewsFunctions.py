from flask import Flask, render_template, request, jsonify 
from .models import db, Player, Game
from .ai import get_move

#Description des paramètres
'''
movement : Dictionnaire indiquant le déplacement du joueur ({"x": ..., "y": ...}), où "x" et "y" représentent le décalage horizontal et vertical respectivement (ex : {"x": 1, "y": 0} pour un pas à droite)
array_string : Chaîne représentant l’état actuel de la grille, où chaque ligne est séparée par un espace. Les cases sont codées par des caractères (ex : '0' pour une case vide, 'x' pour un obstacle, ou un chiffre pour le symbole d'un joueur).
player : Dictionnaire indiquant la position actuelle et le symbole du joueur ({"x": ..., "y": ..., "symbol": ...}).
La fonction utilise ces paramètres pour vérifier si le déplacement est possible en fonction de la grille, des limites et des obstacles.
'''
def is_valid_movement(movement, array_string, player):
    # Convertit array_string en une grille de caractères
    lines = array_string.strip().split(' ')
    grid = [list(line) for line in lines]
    n = len(grid)  # Dimension de la grille
    # Calcule la nouvelle position
    
    new_x = player["x"] + movement["x"]
    new_y = player["y"] + movement["y"]
    # Vérifie les limites de la grille et la présence d'un obstacle
    if not (0 <= new_x < n and 0 <= new_y < n):
        return -1  # Mouvement non autorisé
    
    if grid[new_y][new_x] == 'x' or int(grid[new_y][new_x]) == int( player["symbol"]):
        
        # Mouvement autorisé, mise à jour de la grille
        grid[new_y][new_x] = player["symbol"]  # La nouvelle position prend le symbole du joueur
        
        # Reconstruit array_string avec la grille mise à jour
        modified_array_string = ' '.join(''.join(row) for row in grid)
        # Retourne la nouvelle position et la grille mise à jour
        return new_x, new_y, modified_array_string
    else :
        return -1
    

'''
La fonction prend un paramètre :

- grid_string : une chaîne de caractères représentant l'état actuel de la grille, où chaque case est un caractère ("x" pour un obstacle, "1" pour le joueur 1, "2" pour le joueur 2).
- La fonction vérifie d'abord si des cases "x" sont encore présentes dans la grille, ce qui signifie que la partie n'est pas terminée. Si aucun obstacle "x" n'est trouvé, la fonction compte alors les occurrences des symboles "1" et "2".
- Elle renvoie

1 si le joueur humain ("1") a plus de symboles que l'IA ;
2 si l'IA ("2") en a davantage ;
3 en cas d'égalité
'''
def check_winner(grid_string):
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


import random

def get_move():
    '''
    Renvoie un deplacement aleatoire parmi les directions cardinales :
    droite, gauche, haut ou bas.

    Returns:
        dict: Deplacement avec 'x' et 'y' comme coordonnees.
    '''
    return random.choice([{"x" : 1, "y":0}, {"x":-1, "y":0}, {"x":0, "y":1}, {"x":0 ,"y": -1}])


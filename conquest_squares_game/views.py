from flask import Flask, render_template, request,jsonify
from . import models
from .ai import get_move
from .models import Player, Game, db
import random
import requests

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


@app.route('/start_game', methods=['POST'])
def start_game():
    pass


# Gestion du plateau (on créé le plateau côté serveur)
BOARD_SIZE = 5
gameState = {
    "board": [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
    "posPlayer1": {"x": 0, "y": 0},
    "posPlayer2": {"x": BOARD_SIZE - 1, "y": BOARD_SIZE - 1},
    "currentPlayer": 1
}

# Marquer les positions initiales
gameState["board"][0][0] = "J1"
gameState["board"][BOARD_SIZE - 1][BOARD_SIZE - 1] = "J2"

# Fonction pour vérifier si un mouvement est valide
def isMoveValid(playerPos, x, y):
    distance = abs(playerPos["x"] - x) + abs(playerPos["y"] - y)
    return distance == 1 and gameState["board"][x][y] == ""

# Fonction pour trouver les mouvements valides autour d'une position
def getValidMoves(playerPos):
    x, y = playerPos["x"], playerPos["y"]
    possible_moves = [
        (x - 1, y), (x + 1, y),  # Haut et bas
        (x, y - 1), (x, y + 1)   # Gauche et droite
    ]
    return [(nx, ny) for nx, ny in possible_moves if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and isMoveValid(playerPos, nx, ny)]

# Fonction pour le mouvement aléatoire de l'IA
def aiMove():
    validMove = getValidMoves(gameState["posPlayer2"])
    if validMove:
        x, y = random.choice(validMove)
        gameState["board"][gameState["posPlayer2"]["x"]][gameState["posPlayer2"]["y"]] = ""
        gameState["board"][x][y] = "J2"
        gameState["posPlayer2"] = {"x": x, "y": y}

# On doit créer une route qui va venir récupérer le mouvement via la méthode post (DIFFERENT DU GAME qu'on af ait)
@app.route('/play', methods=['POST'])
def playMove():
    data = request.get_json()
    x, y = data['x'], data['y']
    player = data['player']

    # Vérifie le joueur actuel + retour erreur
    if gameState["currentPlayer"] != player:
        return jsonify({"status": "c'est pas ton tour coco"}), 403

    # Déterminer la position actuelle et la vérification
    if player == 1:
        playerPos = gameState["posPlayer1"]
        if isMoveValid(playerPos, x, y):
            # Mettre à jour le plateau pour le joueur 1
            gameState["board"][playerPos["x"]][playerPos["y"]] = ""
            gameState["board"][x][y] = "J1"
            gameState["posPlayer1"] = {"x": x, "y": y}

            # Passer au joueur 2 (IA) pour un mouvement aléatoire
            gameState["currentPlayer"] = 2
            aiMove()  # Mouvement de l'IA

            # Rendre le tour au joueur 1
            gameState["currentPlayer"] = 1

            return jsonify({"status": "success", "gameState": gameState}), 200
        else:
            return jsonify({"status": "invalid move"}), 400
    else:
        return jsonify({"status": "invalid player"}), 403
from flask_sqlalchemy import SQLAlchemy
import logging as lg
#create database connection object
db = SQLAlchemy()

class Game(db.Model):
    __tablename__ = 'games'

    id_game = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player1_name = db.Column(db.String(100), nullable=False)
    player2_name = db.Column(db.String(100), nullable=False)
    winner = db.Column(db.String(100), nullable=True)  # Peut être NULL si pas encore de gagnant
    moves_played = db.Column(db.Integer, nullable=False)

    def __init__(self, player1_name, player2_name, winner, moves_played, player1_moves, player2_moves):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.winner = winner
        self.moves_played = moves_played

class Move(db.Model):
    __tablename__ = 'moves'

    id_move = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id_game'), nullable=False)
    player = db.Column(db.String(100), nullable=False)  # Peut être "player1" ou "player2"
    x_coordinate = db.Column(db.Integer, nullable=False)  # Coordonnée x (0-4 pour une grille 5x5)
    y_coordinate = db.Column(db.Integer, nullable=False)  # Coordonnée y (0-4 pour une grille 5x5)

    def __init__(self, game_id, player, x_coordinate, y_coordinate):
        self.game_id = game_id
        self.player = player
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    lg.warning('DB initialized !')

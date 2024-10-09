from flask_sqlalchemy import SQLAlchemy
import logging as lg
#create database connection object
db = SQLAlchemy()


class Player(db.Model):
    __tablename__ = 'players'

    id_player = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    is_human = db.Column(db.Boolean, nullable=False)  # True for human, False for AI

    def __init__(self, name, is_human):
        self.name = name
        self.is_human = is_human

class Game(db.Model):
    __tablename__ = 'games'

    id_game = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('players.id_player'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('players.id_player'), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('players.id_player'), nullable=True)
    playerpos1_x = db.Column(db.Integer, nullable=False)
    playerpos1_y = db.Column(db.Integer, nullable=False)
    playerpos2_x = db.Column(db.Integer, nullable=False)
    playerpos2_y = db.Column(db.Integer, nullable=False)

    boxes = db.Column(db.String(25), nullable=True) # une lettre représente une case, 1 pour joueur 1, 2 joueur 2 ,
    # 0 aucun joueur. 25 lettres, lignes espacées par un espace ducoup xxxxx xxxxx xxxxx xxxxx xxxxx

    def __init__(self, player1_id, player2_id, winner):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.winner = winner

def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    lg.warning('DB initialized !')

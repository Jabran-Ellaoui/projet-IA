from flask_sqlalchemy import SQLAlchemy
import logging as lg
#create database connection object
db = SQLAlchemy()


class Player(db.Model):
    __tablename__ = 'player'

    id_player = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    is_human = db.Column(db.Boolean, nullable=False)  # True for human, False for AI

    def __init__(self, name, is_human):
        self.name = name
        self.is_human = is_human

class Game(db.Model):
    __tablename__ = 'game'

    id_game = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id_player'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id_player'), nullable=False)
    current_player = db.Column(db.Integer, db.ForeignKey('player.id_player'), nullable=True)
    playerpos1_x = db.Column(db.Integer, nullable=False)
    playerpos1_y = db.Column(db.Integer, nullable=False)
    playerpos2_x = db.Column(db.Integer, nullable=False)
    playerpos2_y = db.Column(db.Integer, nullable=False)

    boxes = db.Column(db.String(25), nullable=False) # une lettre représente une case, 1 pour joueur 1, 2 joueur 2 ,
    # 0 aucun joueur. 25 lettres, lignes espacées par un espace ducoup xxxxx xxxxx xxxxx xxxxx xxxxx

    def __init__(self, player1_id, player2_id, table_size ):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.playerpos1_x = 1
        self.playerpos1_y = 1
        self.playerpos2_x = table_size
        self.playerpos2_y = table_size
        self.current_player= self.player1_id
        self.boxes = self.boxes = "".join([
                "1" + "x" * (table_size - 1),
                " " + ("x" * table_size + " ") * (table_size - 2), 
                "x" * (table_size - 1) + "2"
        ])
    def apply_movement(self, player_new_x, player_new_y, new_boxes):
        if(self.player1_id == self.current_player):
            self.playerpos1_x = player_new_x
            self.playerpos1_y = player_new_y 
            self.current_player = self.player2_id
        else :
            self.playerpos2_x = player_new_x
            self.playerpos2_y = player_new_y
            self.current_player = self.player1_id

        self.boxes = new_boxes
        db.session.commit() 
        return (self.playerpos1_x, self.playerpos1_y) if self.current_player == self.player1_id else (self.playerpos2_x, self.playerpos2_y)


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("lancéééé")
    lg.warning('DB initialized !')

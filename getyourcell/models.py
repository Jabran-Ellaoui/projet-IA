from flask_sqlalchemy import SQLAlchemy
import logging as lg

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

    boxes = db.Column(db.String(25), nullable=False)

    def __init__(self, player1_id, player2_id, ):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.playerpos1_x = 1
        self.playerpos1_y = 1
        self.playerpos2_x = 5
        self.playerpos2_y = 5
        self.current_player= self.player1_id
        self.boxes = self.boxes = "".join([
                "1" + "x" * (table_size - 1),
                " " + ("x" * table_size + " ") * (table_size - 2), 
                "x" * (table_size - 1) + "2"
        ])

# Create database connection object
db = SQLAlchemy()
def init_db():
 db.drop_all()
 db.create_all()
 db.session.commit()
 lg.warning('Database initialized!')
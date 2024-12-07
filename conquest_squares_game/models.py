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
        self.playerpos1_x = 0
        self.playerpos1_y = 0   
        self.playerpos2_x = table_size -1
        self.playerpos2_y = table_size -1
        self.current_player = self.player1_id
        self.boxes = self.boxes = "".join([
                "1" + "x" * (table_size - 1),
                " " + ("x" * table_size + " ") * (table_size - 2), 
                "x" * (table_size - 1) + "2"
        ])

    def apply_movement(self, player_new_x, player_new_y, new_boxes):
        '''
        La fonction apply_movement prend trois paramètres :

        player_new_x et player_new_y : les nouvelles coordonnées du joueur qui effectue le mouvement.
        new_boxes : la nouvelle configuration de la grille après le mouvement.
        La fonction vérifie quel joueur est le joueur actuel (current_player) et met à jour les coordonnées
        du joueur correspondant . Ensuite, elle passe le tour à l’autre joueur. La grille (boxes) est également
        mise à jour, et les changements sont sauvegardés en base de données.

        La fonction retourne la position actuelle des deux joueurs, en mettant la position du joueur actuel en premier.
        '''
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
        return (self.playerpos1_x, self.playerpos1_y, self.playerpos2_x, self.playerpos2_y) if self.current_player == self.player1_id else (self.playerpos2_x, self.playerpos2_y, self.playerpos1_x, self.playerpos1_y)

class QTable(db.Model):
    __tablename__ = 'q_table'

    state_board = db.Column(db.String(255), primary_key=True)  # L'état du tableau, représenté sous forme de chaîne
    esperance_up = db.Column(db.Float, nullable=True, default=0.0)
    esperance_left = db.Column(db.Float, nullable=True, default=0.0)
    esperance_right = db.Column(db.Float, nullable=True, default=0.0)
    esperance_down = db.Column(db.Float, nullable=True, default=0.0)

    def __init__(self, state_board, esperance_droit=0.0, esperance_gauche=0.0, esperance_haut=0.0, esperance_bas=0.0):
        self.state_board = state_board
        self.esperance_droit = esperance_droit
        self.esperance_gauche = esperance_gauche
        self.esperance_haut = esperance_haut
        self.esperance_bas = esperance_bas

class History(db.Model):
    __tablename__ = 'history'

    id_game = db.Column(db.Integer, primary_key=True )
    id_player = db.Column(db.Integer, primary_key=True)  # Player making the move
    precedent_state_board = db.Column(db.String(255), nullable=False)  # Previous board state as a string    
    precedent_move = db.Column(db.String(20), nullable=False)  # Previous move represented as a stringified tuple (e.g., "(x, y)")
    
    def __init__(self, id_game, precedent_state_board, id_player, precedent_move):
        self.id_game = id_game
        self.precedent_state_board = precedent_state_board
        self.id_player = id_player
        self.precedent_move = precedent_move

def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print("lancéééé")
    lg.warning('DB initialized !')

import os
from conquest_squares_game import models


### CHEMINS DE CONFIGURATIONS ###
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

### PARAMETRES DE JEU ###
TABLE_SIZE = 5
MAX_TURNS = 500


### PARAMETRES IA ###
epsilon = 0.3
ALPHA = 0.1
GAMMA = 0.9
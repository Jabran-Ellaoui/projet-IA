from conquest_squares_game import app
from conquest_squares_game.models import init_db

# Contexte d'application Flask pour exécuter des commandes avec l'application
with app.app_context():
    init_db()
from myApp import app
from myApp.models import init_db

# Contexte d'application Flask pour exécuter des commandes avec l'application
with app.app_context():
    init_db()
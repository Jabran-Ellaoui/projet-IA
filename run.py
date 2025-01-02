from conquest_squares_game import app, init_db
from conquest_squares_game.models import db, Game as game, QTable as qEntries
from flask import Flask
import logging, os, time, sys
from conquest_squares_game.aiTraining import *
from colorama import Fore, Back, Style, init


if __name__ == "__main__":
    logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
    logging.getLogger('flask').setLevel(logging.ERROR)
        
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None

    init()

    print(Fore.GREEN + "[INFO] : Serveur démarré\n")
    with app.app_context():
            nb_games = db.session.query(game).count()
            nb_qentries = db.session.query(qEntries).count()
            print(Fore.YELLOW + f"[INFO] : Nombre de parties jouées : {nb_games}" )
            print(Fore.YELLOW + f"[INFO] : Nombre d'entrées QTable : {nb_qentries}\n")
            #start_training()
    app.run()
 

    

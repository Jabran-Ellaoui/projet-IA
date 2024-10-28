from flask import Flask, render_template
from . import models
<<<<<<< Updated upstream
=======
from .ai import get_move
from .models import Player, Game, db
import random

>>>>>>> Stashed changes
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

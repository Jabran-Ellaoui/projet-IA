from flask import Flask, render_template
from . import models
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

@app.route('/travel_request')# je vais arrêter pour l'instant, et me concentrer sur ma tâche
def travel_request():
    data = request.json # récupére les données du client 

    axe = data.get("axe")
    direction = data.get("direction")
    
    if( axe != "neutral"):
        if(axe == "horizontal"):
            if( < 5): 

            else : 

        else :
            if( < 5 ):

            else : 
    return 

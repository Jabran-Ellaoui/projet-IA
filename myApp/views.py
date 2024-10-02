from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("oui.html")
def content(content_id):
    return content_id
@app.route('/jeu')
def jeu():
    return render_template('jeu.html')

from flask import Flask
from .views import app
from . import models

#connect sqalchemy to app
models.db.init_app(app)

@app.cli.command("init_db")
def init_db():
    with app.app_context():
        init_db()  # Initialize the database
    models.init_db()

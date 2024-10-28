from flask import Flask
from . import models
from .models import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    with app.app_context():
        from . import views, models
        init_db()

    @app.cli.command("init_db")
    def init_db():
        models.init_db()
    return app
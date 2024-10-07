from flask_sqlalchemy import SQLAlchemy
import logging as lg
#create database connection object
db = SQLAlchemy()

def init_db():
    db.drop_all()
    db.create_all()
    ## définir le modéle
    db.session.commit()
    lg.warning('DB initialized !')

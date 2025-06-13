from flask_login import UserMixin
from sqlalchemy.orm import foreign
from datetime import datetime
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email =  db.Column(db.String, unique=True)
    password = db.Column(db.String)
    name = db.Column(db.String)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    question = db.Column(db.String, unique=False)
    answer = db.Column(db.String, unique=False, nullable=True)
    model = db.Column(db.String, unique=False, nullable=True)
   # created_at = db.Column(db.Datetime, default=datetime.utcnow)

#macht der Sinn? wäre eine crud möglichkeit
class Demands(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)





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
    confidence = db.Column(db.Float, nullable=True)
    confidence_grog = db.Column(db.Float, nullable=True)
    confidence_chatgpt = db.Column(db.Float, nullable=True)
   # created_at = db.Column(db.Datetime, default=datetime.utcnow)


class SystemPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=150)





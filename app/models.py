from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    admin = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    current_state = db.relationship('User_State', backref='current_state', lazy='dynamic') # Esto hace que si yo despues tengo un User pitu, si pongo pitu.actual_state.first() me mueste el State de pitu

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

        
    def __repr__(self):
        return '<User Name: {}, Admin: {}>'.format(self.username,self.admin)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User_State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    light_state = db.Column(db.Boolean)
    light_intensity=db.Column(db.Integer)
    temp_state= db.Column(db.Float)

    def __repr__(self):
        return '<State {},Intensity {}, Temp {}>'.format(self.light_state,self.light_intensity,self.temp_state)

class Current_State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    light_state = db.Column(db.Boolean)
    light_intensity=db.Column(db.Integer)
    temp_state= db.Column(db.Float)

    def __repr__(self):
        return '<State {}, Temp {}>'.format(self.light_state,self.temp_state)

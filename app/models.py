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
    user_light_state = db.relationship('User_Light_State', backref='user_light_state', lazy='dynamic') # Esto hace que si yo despues tengo un User pitu, si pongo pitu.actual_state.first() me mueste el State de pitu
    user_temperature_state = db.relationship('User_Temperature_State', backref='user_temperature_state', lazy='dynamic') # Esto hace que si yo despues tengo un User pitu, si pongo pitu.actual_state.first() me mueste el State de pitu

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

        
    def __repr__(self):
        return '<User Name: {}, Admin: {}>'.format(self.username,self.admin)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User_Light_State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64),db.ForeignKey('user.username'), index=True)
    light_state = db.Column(db.Boolean,default=False)
    light_intensity=db.Column(db.Integer,default=50)
    str_id=db.Column(db.String(64),default='default')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    

    def __repr__(self):
        return '<State {},Intensity {}>'.format(self.light_state,self.light_intensity)

class User_Temperature_State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64),db.ForeignKey('user.username'), index=True)
    temp_state=db.Column(db.Boolean,default=False)
    temp_set_point= db.Column(db.Integer, default=20)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

class Current_Light_State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user=db.Column(db.String(64), index=True) #"quien seteo este estado"
    light_state =db.Column(db.Boolean,default=False) 
    light_intensity=db.Column(db.Integer,default=50)
    str_id=db.Column(db.String(64),default='default') #-->"luz cocina","luz patio"
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now) #"Cuando setearon este estado"


    def __repr__(self):
        return '<State {}>'.format(self.light_state)

class Current_Temperature_State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user=db.Column(db.String(64),index=True) #"quien seteo este estado"
    temp_state= db.Column(db.Boolean,default=False)
    temp_set_point=db.Column(db.Integer, default=22)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now) #"Cuando setearon este estado"
    def __repr__(self):
        return '<Temp {}>'.format(self.temp_state)


class Scheduled_events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64),db.ForeignKey('user.username'), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    str_id=db.Column(db.String(64))
    pid=db.Column(db.String(40), index=True, unique=True)


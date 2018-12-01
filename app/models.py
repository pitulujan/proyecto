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

class Devices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_perm=db.Column(db.Boolean,default=False) #False for everyone , True for admins
    str_id=db.Column(db.String(64),default='default') #Luz, motor, etc
    location=db.Column(db.String(64),default='default') #Nombre de la habitacion donde se encuentra el device
    dev_type=db.Column(db.Boolean,default=False) #True para booleano y False no booleano(dimmer)
    state=db.Column(db.Boolean,default=False) #On/Off 
    set_point=db.Column(db.Integer,default=20) #En caso de dev_type=False y está expresado en porcentaje
    def __repr__(self):
        return '<str_id {},location {},dev_type {}>'.format(self.str_id,self.location,self.dev_type)
    

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64),db.ForeignKey('user.username'), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    str_id=db.Column(db.String(64),default='default')
    location=db.Column(db.String(64),default='default')
    description = db.Column(db.String(64),default='Creation')
    def __repr__(self):
        return '<user {},description {}>'.format(self.user,self.description)


class Scheduled_events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64),db.ForeignKey('user.username'), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    str_id=db.Column(db.String(64))
    location=db.Column(db.String(64),default='default')
    pid=db.Column(db.String(40), index=True, unique=True)


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
    dev_type=db.Column(db.Boolean,default=False) #True para booleano y False no booleano(dimmer -> solo la temp por ahora)
    state=db.Column(db.Boolean,default=False) #On/Off 
    set_point=db.Column(db.Integer,default=None) #En caso de dev_type=False y está expresado en porcentaje
    temp_device = db.Column(db.Boolean,default=False)
    mac_address=db.Column(db.String(128),unique=True)
    def __repr__(self):
        return '<str_id {},location {},dev_type {}>'.format(self.str_id,self.location,self.dev_type)

class Sensors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location=db.Column(db.String(64)) #Nombre de la habitacion donde se encuentra el device
    battery = db.Column(db.Boolean,default=True)
    mac_address=db.Column(db.String(128),unique=True)
    last_update=db.Column(db.DateTime,default=datetime.now)
    active_temp_avegare = db.Column(db.Boolean,default=True)
    

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64),db.ForeignKey('user.username'))
    timestamp = db.Column(db.String(32), index=True)
    description = db.Column(db.String(64),default='default')
    def __repr__(self):
        return '<user {},description {}>'.format(self.user,self.description)

class Scheduled_events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64),db.ForeignKey('user.username'), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    str_id=db.Column(db.String(64))
    location=db.Column(db.String(64),default='default')
    event_date=db.Column(db.String(32))
    event_type=db.Column(db.String(8))
    event_cron=db.Column(db.String(32))
    event_param_state=db.Column(db.Boolean,default=False)
    event_param_setpoint=db.Column(db.Integer, default='20')
    pid=db.Column(db.String(40), index=True, unique=True)



from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm 
from app.manage_users import *
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, User_State
from werkzeug.urls import url_parse
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import os
from app.server import set_temp, set_light, get_set_point_temp, get_current_temp, get_initial_values,get_light_state,get_set_point_light

'''
import socket
import sys
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 8888

try:
    soc.connect((host, port))
except:
    print("Connection error")
    sys.exit()
'''
def tick():
    print('Tick! The time is: %s' % datetime.now())
scheduler = BackgroundScheduler()
scheduler.add_job(tick, 'interval', seconds=20)
scheduler.start()
print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))



get_initial_values()
@app.route('/')
@app.route('/index')
@login_required
def index():
	return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=' Log In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.admin != 1:
        flash('In order to add a new user you  must be an Administrator')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        ans=create_user_full(form)
        flash(ans)
        return redirect(url_for('index'))
        
    return render_template('register.html', title=' New User', form=form)


@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    if current_user.admin != 1:
        flash('In order to delete a user you must be an Administrator')
        return redirect(url_for('index'))
    users = User.query.all()

    if request.method == 'POST':
        post_id = request.form.get('delete')
        ans=delete_user_full(post_id)
        flash(ans)
        return redirect(url_for('delete_user'))
    return render_template('delete_user.html', title=' Delete User', users=users)



@app.route('/setparameters', methods=['GET', 'POST'])
@login_required
def setparameters():

    current_temp =get_current_temp()
    current_temp_set_point=get_set_point_temp()

    print(current_temp)
    print(current_temp_set_point)
    
    if request.method == 'POST':
        print(str(request.form.get('set_temp')))
        set_temp(request.form.get('set_temp'),current_user.id)
        flash("The temperature was set in: "+str(request.form.get('set_temp'))+" successfully")
        return redirect(url_for('index'))
        
    return render_template('setparameters.html', title=' Set Temperature', current_temp_set_point=current_temp_set_point, current_temp=current_temp)
#Lo logreeeee lo quiero compartir con mi familia que los amooooo

@app.route('/toggle_switch', methods=['GET', 'POST'])
@login_required
def toggle_switch():

    current_light_set_point=get_set_point_light()
    if get_light_state():
        current_state='On'
        button='Turn Light Off'
        
    else:
        current_state='Off'
        button='Turn Light On'
        
        
    if request.method == 'POST':
        if request.form.get('statevalue')=='On':
            set_light(True,current_user.id,request.form.get('set_point_light'))
            hola="The Light was set in: "+str(request.form.get('set_point_light'))+" successfully"
        else:
            set_light(False,current_user.id)
            hola="Light was successfully turned off"
        
        flash(hola)
        return redirect(url_for('toggle_switch'))
        
    return render_template('toggle_switch.html', title=' Set light', current_light_set_point=current_light_set_point, current_state=current_state,button=button)
#Lo logreeeee lo quiero compartir con mi familia que los amooooo

@app.route('/base2', methods=['GET', 'POST'])
@login_required
def base2():
	return render_template('base2.html')


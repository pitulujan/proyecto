
from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm 
from app.manage_users import *
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime
from app.server import set_temp, set_light, get_temp_state, get_initial_values,get_light_state




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
        print(post_id)
        ans=delete_user_full(post_id)
        flash(ans)
        return redirect(url_for('delete_user'))
    return render_template('delete_user.html', title=' Delete User', users=users)



@app.route('/set_temperature', methods=['GET', 'POST'])
@login_required
def set_temperature():

    current_temp_state =get_temp_state() # VER QUE LE MANDO AL TEMPLATE; SI EL ESTADO O EL DIC
    
    if request.method == 'POST':
        print(request.form.get('statevalue'),type(request.form.get('statevalue')))
        if request.form.get('statevalue')=='True':
            print(request.form.get('statevalue'))
            set_temp(True,request.form.get('set_temp'),current_user.username)
            flash("The temperature was set in: "+str(request.form.get('set_temp'))+" successfully")
            return redirect(url_for('index'))
        else:
            set_temp(False,request.form.get('set_temp'),current_user.username)

    return render_template('set_temperature.html', title=' Set Temperature', dic=current_temp_state)
#Lo logreeeee lo quiero compartir con mi familia que los amooooo

@app.route('/toggle_switch', methods=['GET', 'POST'])
@login_required
def toggle_switch():

    current_light_state =get_light_state()#-->puedo pasar un dic y que jinja2 se encargue de lo suyo atr perri
          
        
    if request.method == 'POST':
        if request.form['state'] == 'True':
            set_light(True,request.form['set_point'],current_user.username,request.form['place'])
        else:
            set_light(False,request.form['set_point'],current_user.username,request.form['place'])

        print(request.form['place'],request.form['state'],request.form['set_point'])
        

    return render_template('set_lights.html', title=' Set light', dic=current_light_state)
#Lo logreeeee lo quiero compartir con mi familia que los amooooo





from flask import render_template, flash, redirect, request, url_for,jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm, ChangePassword
from app.manage_users import *
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime
from app.server import set_temp, set_light, get_temp_state, get_initial_values,get_light_state




#get_initial_values()
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

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        change= change_user_password(form,current_user.username)
        if change == False:
            flash('Invalid Current Password')
            return redirect(url_for('change_password'))
        elif change== True:
            flash('Your new password should be different from the current one')
            return redirect(url_for('change_password'))
        else:
            flash(change)
            return redirect(url_for('logout'))
    return render_template('change_password.html',title='Change Password',form=form)


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
        
        if request.form['state']=='True':
            
            set_temp(True,request.form['set_point'],current_user.username)
                        
        else:
            set_temp(False,request.form['set_point'],current_user.username)

    return render_template('set_temperature.html', title=' Set Temperature', dic=current_temp_state)
#Lo logreeeee lo quiero compartir con mi familia que los amooooo

@app.route('/set_lights', methods=['GET', 'POST'])
@login_required
def set_lights():

    current_light_state =get_light_state()#-->puedo pasar un dic y que jinja2 se encargue de lo suyo atr perri
          
        
    if request.method == 'POST':
    
        if request.form['state'] == 'True':
            set_light(True,request.form['set_point'],current_user.username,request.form['place'])

        else:
            set_light(False,request.form['set_point'],current_user.username,request.form['place'])
        
        

    return render_template('set_lights.html', title=' Set lights', dic=current_light_state)

#Lo logreeeee lo quiero compartir con mi familia que los amooooo

@app.route('/schedule_events', methods=['GET', 'POST'])
@login_required
def schedule_events():

    if request.method == 'POST':

        print(request.form.get('mail'),request.form.get('pass'))
    return render_template('schedule_events.html', title=' Schedule Events')

@app.route('/pruebitas', methods=['GET', 'POST'])
@login_required
def pruebitas():
    rec_dict=['Hi,', "I'm", 'Jim', 'Martin.', "I'm", 'managing', 'director', 'and', 'our', 'federal', 'tax', 'services', 'group', 'did', 'uniform', 'compensation', 'or', 'unicab', 'falls', 'under', 'Section', '263', 'a', 'report', 'taxpayers', 'to', 'capitalize', 'direct', 'and', 'indirect', 'cost', 'to', 'pop', 'reproduce', 'some', 'property', 'of', 'our', 'pre', 'sale', 'one', 'type', 'of', 'cost', 'to', 'has', 'to', 'be', 'capitalized', 'is', 'the', 'book', 'packs', 'difference', 'in', 'cost', 'that', 'relate', 'to', 'the', 'the', 'property', "that's", 'producer', 'crock', 'for', 'resale.', 'So', 'for', 'example', 'bonus', 'depreciation,', "it's", 'awesome', 'a', 'jerk', 'off', 'that', 'tax', 'payers', 'will', 'cap', 'lies', 'under', 'the', 'unit', 'Camp', 'rules', 'and', 'with', 'the', 'new', '100%', 'bonus', 'depreciation', 'rules', 'as', 'well', 'sort', 'of', 'tax', 'form.', 'Thanks,', 'Chris', 'Kattan', 'up', 'type', 'lodging', 'a', 'significant', 'amount', 'of', 'bonus', 'depreciation', 'to', 'ending', 'inventory', 'one', 'way', 'to', 'avoid.', 'This', 'is', 'to', "Lexi's", 'store', 'from', 'the', 'ratio', 'or', 'heart', 'message.', 'So', 'for', 'taxpayers', 'using', 'a', 'simple', '5', 'production', 'method', 'or', 'simple', '5', 'resale', 'message,', 'the', 'higher', 'election', 'could', 'significantly', 'reduce', 'the', 'amount', 'of', 'cost', 'Half-Life', '2', 'ending', 'inventory', 'under', 'the', 'you', 'bye', 'excluding', 'bonus', 'depreciation', 'from', 'the', 'cost', 'of', 'a', 'capitalized']
    if request.method == 'POST':
        answer='Hola anto, apretaste el ' + request.form['id']+ ' guachita'
        return jsonify({'answer': answer})
    return render_template('pruebitas.html',rec_dict=rec_dict)

@app.route('/pruebitas2', methods=['GET', 'POST'])
@login_required
def pruebitas2():
    
    if request.method == 'POST':
        return jsonify({'nombre': 'pitu', 'apellido' : 'Lujan'})
    return render_template('pruebitas2.html')

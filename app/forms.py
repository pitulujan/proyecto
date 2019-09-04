from flask_wtf import FlaskForm
from app.models import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField,DecimalField , IntegerField, validators
from wtforms.validators import ValidationError, DataRequired, EqualTo , NumberRange 
from wtforms.fields.html5 import EmailField

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), validators.Length(min=4,max=10)])
    password = PasswordField('Contraseña', validators=[DataRequired(), validators.Length(min=4,max=10)])
    password2 = PasswordField('Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    email = EmailField('Email', validators=[validators.DataRequired(), validators.Email()])
    email2 = EmailField('Repetir Email', validators=[validators.DataRequired(), validators.Email(),EqualTo('email')])
    admin = BooleanField('Administrador')
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor utilice otro nombre de usuario')

class ChangePassword(FlaskForm):
    current_password=PasswordField('Current Password', validators=[DataRequired(), validators.Length(min=4,max=10)])
    new_password=PasswordField('New Password', validators=[DataRequired(), validators.Length(min=4,max=10)])
    check_new_password=PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

from flask_wtf import FlaskForm
from app.models import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField,DecimalField , IntegerField, validators
from wtforms.validators import ValidationError, DataRequired, EqualTo , NumberRange 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), validators.Length(min=4,max=10)])
    password = PasswordField('Password', validators=[DataRequired(), validators.Length(min=4,max=10)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField('Administrator')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class ChangePassword(FlaskForm):
    current_password=PasswordField('Current Password', validators=[DataRequired(), validators.Length(min=4,max=10)])
    new_password=PasswordField('New Password', validators=[DataRequired(), validators.Length(min=4,max=10)])
    check_new_password=PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

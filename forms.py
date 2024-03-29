from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, InputRequired, EqualTo, Length

class AddAccountForm(FlaskForm):
    login = StringField("Login", validators=[Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków"),InputRequired("Login nie może być pusty")])
    password = PasswordField("Password", validators=[InputRequired("Hasło nie może być puste"), Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków"), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField("Powtórz hasło")
    email = StringField("Email", validators=[Length(max=128, message="Email nie może mieć więcej niż 128 znaków"),Email("Proszę wprowadzić poprawny adres email")])
    submit = SubmitField("Wyślij")

class DeleteAccountForm(FlaskForm):
    submit = SubmitField('Delete')

class LoginForm(FlaskForm):
    login = StringField("Login", validators=[Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków"),InputRequired("Login nie może być pusty")])
    password = PasswordField("Password", validators=[InputRequired("Hasło nie może być puste"), Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    submit = SubmitField("Zaloguj się")
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, InputRequired, EqualTo, Length, Optional

class AddAccountForm(FlaskForm): # User
    login = StringField("Login", validators=[Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków")])
    password = PasswordField("Password", validators=[Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków"), EqualTo('confirm_password', message='Pola hasło i powtórz hasło nie są identyczne')])
    confirm_password = PasswordField("Powtórz hasło")
    email = StringField("Email", validators=[Email("Proszę wprowadzić poprawny adres email"),Length(max=128, message="Email nie może mieć więcej niż 128 znaków")])
    submit = SubmitField("Wyślij")

class RemoveAccountForm(FlaskForm): # Admin
    submit = SubmitField('Delete')

class ChangeAccountForm(FlaskForm): # Admin
    login = StringField("Login", validators=[Optional(),Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków")])
    password = PasswordField("Password", validators=[Optional(),Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    email = StringField("Email", validators=[Optional(),Length(max=128, message="Email nie może mieć więcej niż 128 znaków"),Email("Proszę wprowadzić poprawny adres email")])
    submit = SubmitField("Wyślij")

class ChangeAccountCredentialsForm(FlaskForm): # User
    login = StringField("Login", validators=[Optional(),Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków")])
    password = PasswordField("Password", validators=[Optional(),Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    email = StringField("Email", validators=[Optional(),Length(max=128, message="Email nie może mieć więcej niż 128 znaków"),Email("Proszę wprowadzić poprawny adres email")])
    old_password = PasswordField("Password", validators=[InputRequired("Stare hasło musi zostać wpisane by potwierdzić akcję"),Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    submit = SubmitField("Wyślij")

class LoginForm(FlaskForm): # User
    login = StringField("Login", validators=[Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków")])
    password = PasswordField("Password", validators=[Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    submit = SubmitField("Zaloguj się")

class VerifyActionForm(FlaskForm): # User
    password = PasswordField("Password", validators=[Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    submit = SubmitField("Potwierdź")
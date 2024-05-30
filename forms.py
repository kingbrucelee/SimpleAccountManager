from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, InputRequired, EqualTo, Length, Optional

class AddAccountForm(FlaskForm): # User Create
    login = StringField("Login", validators=[Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków")])
    password = PasswordField("Password", validators=[Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków"), EqualTo('confirm_password', message='Pola hasło i powtórz hasło nie są identyczne')])
    confirm_password = PasswordField("Powtórz hasło")
    email = StringField("Email", validators=[Email("Proszę wprowadzić poprawny adres email"),Length(max=128, message="Email nie może mieć więcej niż 128 znaków")])
    submit = SubmitField("Wyślij")

class AddCourseForm(FlaskForm):
    name = StringField("Name", validators=[Length(min=3, max=64, message="Nazwa Kursu powinna mieć pomiędzy 3 a 64 znaków")])
    description = StringField("Login", validators=[Optional(),Length(min=3, max=256, message="Opis powinien mieć pomiędzy 3 a 256 znaków")])
    submit = SubmitField("Wyślij")

class AuthorizeTeacherForm(FlaskForm):
    pass

class EnrollStudentForm(FlaskForm):
    pass

class AddTaskForm(FlaskForm):
    pass

class AddGradeForm(FlaskForm):
    pass

class ChangeAccountCredentialsForm(FlaskForm): # User Change
    login = StringField("Login", validators=[Optional(),Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków")])
    password = PasswordField("Password", validators=[Optional(),Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    email = StringField("Email", validators=[Optional(),Length(max=128, message="Email nie może mieć więcej niż 128 znaków"),Email("Proszę wprowadzić poprawny adres email")])
    old_password = PasswordField("Password", validators=[InputRequired("Stare hasło musi zostać wpisane by potwierdzić akcję"),Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    submit = SubmitField("Wyślij")

class DeleteCourseForm(FlaskForm):
    pass

class DeleteTaskForm(FlaskForm):
    pass

class DeleteGradeForm(FlaskForm):
    pass

class EditCourseForm(FlaskForm):
    pass

class EditTaskForm(FlaskForm):
    pass

class EditGradeForm(FlaskForm):
    pass

class KickStudentForm(FlaskForm):
    pass

class KickTeacherForm(FlaskForm):
    pass

class LoginForm(FlaskForm): # User Login
    login = StringField("Login", validators=[Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków")])
    password = PasswordField("Password", validators=[Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    submit = SubmitField("Zaloguj się")

class VerifyActionForm(FlaskForm): # User Delete (or any that requires retyping password to confirm)
    password = PasswordField("Password", validators=[Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    submit = SubmitField("Potwierdź")

### Admin Forms Below
class ChangeAccountForm(FlaskForm): # Admin Change
    login = StringField("Login", validators=[Optional(),Length(min=3, max=64, message="Login powinien mieć pomiędzy 3 a 64 znaków")])
    password = PasswordField("Password", validators=[Optional(),Length(min=8, max=64, message="Hasło powinno mieć pomiędzy 8 a 64 znaków")])
    email = StringField("Email", validators=[Optional(),Length(max=128, message="Email nie może mieć więcej niż 128 znaków"),Email("Proszę wprowadzić poprawny adres email")])
    submit = SubmitField("Wyślij")

# Possible rename to "ClickToConfirmForm" to be more universal
class RemoveAccountForm(FlaskForm): # Admin Remove
    submit = SubmitField('Delete')
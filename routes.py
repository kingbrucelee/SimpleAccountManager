from app import app, db
from flask import render_template,redirect,url_for, flash, get_flashed_messages, session,request
from models import User
import forms
import secrets
from pyargon2 import hash
from functools import wraps
import flask
import os # For getting the enviromental variable

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" in flask.session:
            user = User.query.get(session["user_id"])
            if user:
                return(f(user,*args, **kwargs))
            else:
                session.clear()
                return redirect(url_for("login"))
        else:
            flash("Nie jesteś zalogowany, zaloguj się lub utwórz konto","error")
            return redirect(url_for("login"))
    return wrapper

@app.route('/')
@app.route("/account")
@login_required
def account(user):
    user_courses = user.courses
    return render_template("account.html", user=user, courses=user_courses)

@app.route('/create', methods=["GET","POST"]) # Bulk account creation is cringe so there's no admin route of creation
def create():
    form = forms.AddAccountForm()
    if form.validate_on_submit():
        salt = secrets.token_urlsafe(64)
        check = User.query.filter_by(login=form.login.data).first()
        if check:
            flash("Nazwa użytkownika jest zajęta") 
            return render_template("create.html",form=form)   
        user = User(login=form.login.data, password=hash(form.password.data,salt), salt=salt, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash("Konto zostało utworzone")
        session["user_id"] = user.id
        return redirect(url_for("account"))
    return render_template("create.html", form=form)

@app.route("/change_credentials", methods=["GET","POST"]) # User Change
@login_required
def change_credentials(user):
    form = forms.ChangeAccountCredentialsForm()
    if form.validate_on_submit():
        password_entered = hash(form.old_password.data,user.salt)
        if password_entered == user.password:
            if form.login.data:
                check = User.query.filter_by(login=form.login.data).first()
                if check:
                    flash("Nazwa użytkownika jest zajęta") 
                    return render_template("change_credentials.html",form=form)   
                user.login = form.login.data
            if form.email.data:
                check = User.query.filter_by(login=form.login.data).first()
                if check:
                    flash("Email był już wykorzystany przy tworzeniu konta.")
                    db.session.rollback() 
                    return render_template("change_credentials.html",form=form)           
                user.email = form.email.data    
            if form.password.data:
                salt = secrets.token_urlsafe(64)
                user.password = hash(form.password.data,salt)    
                user.salt = salt
                db.session.commit()
                flash("Poświadczenia zostały zmienione")
                return redirect(url_for("account"))
            flash("Błędne stare hasło")
    else:
        return render_template("change_credentials.html", form=form)
    return render_template("change_credentials.html", form=form)
@app.route('/delete_account', methods=['GET',"POST"]) # User Delete
@login_required
def delete_account(user):
    form = forms.VerifyActionForm()
    if form.validate_on_submit():
        password_entered = hash(form.password.data,user.salt)
        if password_entered == user.password:
            db.session.delete(user)
            db.session.commit()
            flash('Konto zostało usunięte')
            return redirect(url_for("login"))
        else:
            flash("Błędne hasło")
    else:
        return render_template("delete_account.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user:
            password_entered = hash(form.password.data,user.salt)
            if password_entered == user.password:
                session["user_id"] = user.id
                flash("Zalogowano pomyślnie", "success")
                return redirect(url_for("account"))
        flash("Błędny login lub hasło", "error")
    return render_template("login.html", form=form)

### Teacher Routes Below
def teacher(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Check whether is_teacher true 
        if 2==2:
            return(f(*args, **kwargs))
        else:
            flash("Nie jesteś nauczycielem","error")
            return redirect(url_for("account"))
    return wrapper

### Admin Routes Below

def admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.cookies.get('admin')==os.environ.get('DATABASE_KEY', 'obraz_szklanka_szafa'):
            return(f(*args, **kwargs))
        else:
            flash("You are not in sudoers file. This incident will be reported")
            return redirect(url_for("account"))
    return wrapper

@app.route('/admin_panel')
@admin
def admin_panel():
    users = User.query.all() 
    return render_template("admin_panel.html", users=users)

@app.route("/change/<int:user_id>", methods=["GET","POST"]) # Admin Change
@admin
def change(user_id):
    user = User.query.get(user_id)
    form = forms.ChangeAccountForm()
    if user:
        if form.validate_on_submit():
            if form.login.data:
                check = User.query.filter_by(login=form.login.data).first()
                if check:
                    flash("Nazwa użytkownika jest zajęta") 
                    return render_template("change.html",form=form,user_id=user_id)          
                user.login = form.login.data
            if form.password.data:
                salt = secrets.token_urlsafe(64)
                user.password = hash(form.password.data,salt)    
                user.salt = salt
            if form.email.data:
                check = User.query.filter_by(email=form.email.data).first()
                if check:
                    flash("Email był już wykorzystany przy tworzeniu konta.")
                    db.session.rollback()
                    return render_template("change.html",form=form, user_id=user_id)   
                user.email = form.email.data
            db.session.commit()
            flash("Poświadczenia zostały zmienione")
            return redirect(url_for("admin_panel"))
        return render_template("change.html",form=form, user_id=user_id)
    flash(f"Użytkownik o numerze {user_id} nie istnieje")
    return redirect(url_for("admin_panel"))

@app.route('/delete/<int:user_id>', methods=['GET', 'POST']) # Admin Delete
@admin
def delete(user_id):
    form = forms.RemoveAccountForm()
    user = User.query.get(user_id)
    if user:
        if form.validate_on_submit():
            if form.submit.data:
                db.session.delete(user)
                db.session.commit()
                flash('Konto zostało usunięte')
            return redirect(url_for('admin_panel'))
        return render_template('delete.html', form=form, user_id=user_id, login=user.login)
    flash(f"Użytkownik o numerze {user_id} nie istnieje")
    return redirect(url_for('admin_panel'))

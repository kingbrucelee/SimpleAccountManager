from app import app, db
from flask import render_template,redirect,url_for, flash, get_flashed_messages, session,abort
from models import User
import forms
import secrets
from pyargon2 import hash
from functools import wraps
import flask

# Teoretycznie można od razu też (if user) dać wraz z lookupem w bazie
# index.html już nie będzie potrzebny
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" in flask.session:
            return(f(*args, **kwargs))
        else:
            flash("Nie jesteś zalogowany, zaloguj się lub utwórz konto","error")
            return redirect(url_for("login"))
    return wrapper

@app.route('/')
@app.route("/account")
@login_required
def account():
    user = User.query.get(session['user_id'])
    if user:
        return render_template("account.html", user=user)
    else:
        session.clear()
        return redirect(url_for("login"))

@app.route('/admin')
def admin():
    users = User.query.all() 
    return render_template("admin.html", users=users)


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

@app.route('/create', methods=["GET","POST"]) # Bulk account creation is cringe so there's no admin route of creation
def create():
    form = forms.AddAccountForm()
    if form.validate_on_submit():
        salt = secrets.token_urlsafe(64)
        user = User(login=form.login.data, password=hash(form.password.data,salt), salt=salt, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash("Konto zostało utworzone")
        session["user_id"] = user.id
        return redirect(url_for("account"))
    return render_template("create.html", form=form)

@app.route("/change/<int:user_id>", methods=["GET","POST"]) # Admin Change
def change(user_id):
    user = User.query.get(user_id)
    form = forms.ChangeAccountForm()
    if user:
        if form.validate_on_submit():
            if form.login.data:
                user.login = form.login.data
            if form.password.data:
                salt = secrets.token_urlsafe(64)
                user.password = hash(form.password.data,salt)    
                user.salt = salt
            if form.email.data:
                user.email = form.email.data
            db.session.commit()
            flash("Poświadczenia zostały zmienione")
            return redirect(url_for("admin"))
        return render_template("change.html",form=form, user_id=user_id)
    flash(f"Użytkownik o numerze {user_id} nie istnieje")
    return redirect(url_for("admin"))

@app.route("/change_credentials", methods=["GET","POST"]) # User Change
@login_required
def change_credentials():
    user = User.query.get(session["user_id"])
    form = forms.ChangeAccountCredentialsForm()
    if user:
        if form.validate_on_submit():
            password_entered = hash(form.old_password.data,user.salt)
            if password_entered == user.password:
                if form.login.data:
                    user.login = form.login.data
                if form.password.data:
                    salt = secrets.token_urlsafe(64)
                    user.password = hash(form.password.data,salt)    
                    user.salt = salt
                if form.email.data:
                    user.email = form.email.data
                db.session.commit()
                flash("Poświadczenia zostały zmienione")
                return redirect(url_for("account"))
            flash("Błędne stare hasło")
        else:
            return render_template("change_credentials.html", form=form)
    else:
        session.clear()
        return redirect(url_for("login"))

@app.route('/delete/<int:user_id>', methods=['GET', 'POST']) # Admin Delete
def delete(user_id):
    form = forms.RemoveAccountForm()
    user = User.query.get(user_id)
    if user:
        if form.validate_on_submit():
            if form.submit.data:
                db.session.delete(user)
                db.session.commit()
                flash('Konto zostało usunięte')
            return redirect(url_for('admin'))
        return render_template('delete.html', form=form, user_id=user_id, login=user.login)
    flash(f"Użytkownik o numerze {user_id} nie istnieje")
    return redirect(url_for('admin'))

@app.route('/delete_account', methods=['GET',"POST"]) # User Delete
@login_required
def delete_account():
    form = forms.VerifyActionForm()
    user = User.query.get(session["user_id"])
    if user:
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
    else:
        session.clear()
        return redirect(url_for("login"))

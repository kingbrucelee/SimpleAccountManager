from app import app, db
from flask import render_template,redirect,url_for, flash, get_flashed_messages, session
from models import User
import forms
import secrets
from pyargon2 import hash

@app.route('/')
@app.route("/account")
def account():
    if "user_id" in session:
        user = User.query.get(session['user_id'])
        if user:
            return render_template("account.html", user=user)
    return render_template("index.html")

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

@app.route('/create', methods=["GET","POST"])
def create():
    form = forms.AddAccountForm()
    if form.validate_on_submit():
        salt = secrets.token_urlsafe(64)
        u = User(login=form.login.data, password=hash(form.password.data,salt), salt=salt, email=form.email.data)
        db.session.add(u)
        db.session.commit()
        flash("Konto zostało utworzone")
        print("Username", form.login.data)
        print("Password", form.password.data)
        print("Email", form.email.data)
        return redirect(url_for("admin"))
    return render_template("create.html", form=form)

@app.route("/change/<int:user_id>", methods=["GET","POST"])
def change(user_id):
    user = User.query.get(user_id)
    form = forms.AddAccountForm()
    if user:
        if form.validate_on_submit():
            salt = secrets.token_urlsafe(64)
            user.login = form.login.data
            user.password = hash(form.password.data,salt)
            user.salt = salt
            user.email = form.email.data
            db.session.commit()
            flash("Poświadczenia zostały zmienione")
            return redirect(url_for("admin"))

        form.login.data = user.login
        form.email.data = user.email
        return render_template("change.html",form=form, user_id=user_id)
    flash(f"Użytkownik o numerze {user_id} nie istnieje")
    return redirect(url_for("admin"))

@app.route('/delete/<int:user_id>', methods=['GET', 'POST'])
def delete(user_id):
    form = forms.DeleteAccountForm()
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

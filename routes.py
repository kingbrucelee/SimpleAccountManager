from app import app, db
from flask import render_template,redirect,url_for, flash, get_flashed_messages, session,request
from models import User, Course, Enrollment, Permission
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

@app.route("/courses", methods=["GET","POST"])
@login_required
def get_courses(user):
    courses= Course.query.all()
    course_data = [{'id': course.id, 'name': course.name, 'description': course.description} for course in courses]

    return render_template("courses.html",courses=course_data,user=user)

@app.route('/create_account', methods=["GET","POST"]) # Bulk account creation is cringe so there's no admin route of creation
def create_account():
    form = forms.AddAccountForm()
    if form.validate_on_submit():
        salt = secrets.token_urlsafe(64)
        check = User.query.filter_by(login=form.login.data).first()
        if check:
            flash("Nazwa użytkownika jest zajęta") 
            return render_template("create_account.html",form=form)   
        user = User(login=form.login.data, password=hash(form.password.data,salt), salt=salt, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash("Konto zostało utworzone")
        session["user_id"] = user.id
        return redirect(url_for("account"))
    return render_template("create_account.html", form=form)

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
@app.route('/logout')
@login_required
def logout(user):
    session.clear()
    flash("Zostałeś wylogowany", "success")
    return redirect(url_for('login'))
### Courses Routes Below
@app.route('/join_course/<int:course_id>')
@login_required
def join_course(user,course_id):
    enrollment = Enrollment(user_id = user.id,course_id= course_id )
    existing_enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()
    if existing_enrollment:
        flash("Jesteś już zapisany na ten kurs.")
        return redirect(url_for('get_courses'))
    else:
        db.session.add(enrollment)
        db.session.commit()
        flash("Zapisano")
        return redirect(url_for('get_courses'))

@app.route("/create_course",methods=["GET","POST"])
#@login_required
def create_course():
    form = forms.AddCourseForm()
    if form.validate_on_submit():
        course = Course(name=form.name.data, description=form.description.data)
        db.session.add(course)
        # Powinna dawać permisje od razu osobie tworzącej ale szczerze nie wiem jak course_id wziąć) 
        #permission = Permission(teacher_id=user.id, course_id=)
        db.session.commit()
        flash("Kurs został utworzony")
    return render_template("create_course.html", form=form)
### Teacher Routes Below
# To oczywiście skrót myślowy i powinno sprawdzać czy masz uprawnienia do kursu (w tabeli permission)
def teacher(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
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

@app.route('/backdoor/<int:user_id>', methods=['GET','POST']) # Admin Login
@admin
def backdoor(user_id):
    session["user_id"] = user_id
    flash("Zalogowano pomyślnie", "success")
    return redirect(url_for("account"))


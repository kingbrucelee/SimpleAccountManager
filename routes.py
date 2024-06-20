from app import app, db
from flask import render_template,redirect,url_for, flash, get_flashed_messages, session,request
from models import User, Course, Enrollment, Permission, Task, TaskResponse, Grade
import forms
import secrets
from datetime import datetime
from pyargon2 import hash
from functools import wraps
import flask
import os
from werkzeug.utils import secure_filename
import os # For getting the enviromental variable
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif','zip','rar'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    coursesT = 0
    if user.is_teacher:
        coursesT = Course.query.join(Permission, (Permission.course_id == Course.id)).filter(
            Permission.teacher_id == user.id).all()
    user_courses = user.courses
    return render_template("account.html", user=user, courses=user_courses, coursesT=coursesT)

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
        if User.query.filter_by(login=form.login.data).first():
            flash("Nazwa użytkownika jest zajęta") 
            return render_template("create_account.html",form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash("Email był już wykorzystany")
            return render_template("create_account.html",form=form)
        
        user = User(login=form.login.data, password=hash(form.password.data,salt), salt=salt, email=form.email.data, is_teacher=form.teacher.data)
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
                    return render_template("change_credentials.html",form=form, user=user)   
                user.login = form.login.data
            if form.email.data:
                check = User.query.filter_by(email=form.email.data).first()
                if check:
                    flash("Email był już wykorzystany przy tworzeniu konta.")
                    db.session.rollback() 
                    return render_template("change_credentials.html",form=form, user=user)           
                user.email = form.email.data    
            if form.password.data:
                salt = secrets.token_urlsafe(64)
                user.password = hash(form.password.data,salt)    
                user.salt = salt
            user.is_teacher=form.teacher.data
            db.session.commit()
            flash("Poświadczenia zostały zmienione")
            return redirect(url_for("account"))
        flash("Błędne stare hasło")
    else:
        return render_template("change_credentials.html", form=form, user=user)
    return render_template("change_credentials.html", form=form, user=user)
@app.route('/delete_account', methods=['GET',"POST"]) # User Delete
@login_required
def delete_account(user):
    # Aktualnie nie usuwa odpowiedzi na zadania i ocen   
    form = forms.VerifyActionForm()
    if form.validate_on_submit():
        password_entered = hash(form.password.data,user.salt)
        if password_entered == user.password:
            permissions = Permission.query.filter_by(teacher_id=user.id).all()
            enrollments = Enrollment.query.filter_by(user_id=user.id).all()            
            for permission in permissions:
                db.session.delete(permission)
            for enrollment in enrollments:
                db.session.delete(enrollment)
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
    existing_enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()
    if existing_enrollment:
        flash("Jesteś już zapisany na ten kurs.")
        return redirect(f"/course/{course_id}")
    else:
        enrollment = Enrollment(user_id = user.id,course_id= course_id )
        db.session.add(enrollment)
        db.session.commit()
        flash("Zapisano")
        return redirect(url_for('get_courses'))

@app.route("/create_course",methods=["GET","POST"])
@login_required
def create_course(user):
    form = forms.AddCourseForm()
    if form.validate_on_submit():
        course = Course(name=form.name.data, description=form.description.data)
        db.session.add(course)
        db.session.commit() # Redundant       
        permission = Permission(teacher_id=user.id, course_id=course.id)
        db.session.add(permission)
        db.session.commit()
        flash("Kurs został utworzony")
        join_course(course.id)
    return render_template("create_course.html", form=form, user=user)

@app.route('/course/<int:course_id>')
@login_required
def view_course(user, course_id):
    course = Course.query.get(course_id)
    if not course:
        flash("Kurs nie istnieje", "error")
        return redirect(url_for('get_courses'))

    tasks = Task.query.filter_by(course_id=course_id).all()
    enrolled_users = Enrollment.query.filter_by(course_id=course_id).all()
    enrolled_user_ids = [enrollment.user_id for enrollment in enrolled_users]
    is_user_enrolled = user.id in enrolled_user_ids
    is_teacher = Permission.query.filter_by(course_id=course.id, teacher_id=user.id).first() is not None
    return render_template("course.html", course=course, tasks=tasks, user=user, is_user_enrolled=is_user_enrolled, is_teacher=is_teacher)

@app.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(user, course_id):
    course = Course.query.get(course_id)
    if not course:
        flash("Kurs nie istnieje", "error")
        return redirect(url_for('get_courses'))
    
    permission = Permission.query.filter_by(course_id=course.id, teacher_id=user.id).first()    
    if not permission:
        flash("Nie możesz usunąć kursu.", "error")
        return redirect(url_for('view_course', course_id=course.id))
    db.session.delete(permission)
    
    enrollments = Enrollment.query.filter_by(course_id=course.id)
    for enrollment in enrollments:
        db.session.delete(enrollment)
    
    tasks = Task.query.filter_by(course_id=course.id)
    for task in tasks:
        grades = Grade.query.filter_by(task_id=task.id)
        responses = TaskResponse.query.filter_by(task_id=task.id)
        for response in responses:
            db.session.delete(response)
        for grade in grades:            
            db.session.delete(grade)
        db.session.delete(task)
    
    db.session.delete(course)    
    db.session.commit()
    flash("Kurs usunięto", "success")
    return redirect(url_for('get_courses'))

@app.route('/create_task/<int:course_id>', methods=['GET', 'POST'])
@login_required
def create_task(user, course_id):
    course = Course.query.get(course_id)
    if not course:
        flash("Kurs nie istnieje", "error")
        return redirect(url_for('get_courses'))
    permission = Permission.query.filter_by(course_id=course.id, teacher_id=user.id).first()

    if not permission:
        flash("Nie masz uprawnień by dodawać zadania.", "error")
        return redirect(url_for('view_course', course_id=course.id))

    form = forms.AddTaskForm()
    if form.validate_on_submit():
        task = Task( course_id=course.id,name=form.name.data, description=form.description.data, finish_date=form.due_date.data)
        db.session.add(task)
        db.session.commit()
        flash("Utworzono zadanie.", "success")
        return redirect(url_for('view_course', course_id=course.id))
    
    return render_template("create_task.html", form=form, course=course)


@app.route('/task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def task(user, task_id):
    task = Task.query.get(task_id)
    if not task:
        flash("Zadanie nie istnieje", "error")
        return redirect(url_for('get_courses'))
    course = task.course
    form = forms.TaskResponseForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = None
        if file:
            original_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{original_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(file_path)
                flash("File uploaded successfully.", "success")
            except Exception as e:
                flash(f"Failed to save file. Error: {e}", "error")
                return redirect(url_for('task', task_id=task.id))
        response = TaskResponse(
            content=form.content.data,
            task_id=task.id,
            user_id=user.id,
            file_path=filename,
            submitted_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(response)
        db.session.commit()
        flash("Wysłano zadanie.", "success")
        return redirect(url_for('task', task_id=task.id))

    is_teacher = Permission.query.filter_by(course_id=course.id, teacher_id=user.id).first() is not None
    if is_teacher:
        responses = TaskResponse.query.filter_by(task_id=task.id)
        return render_template("task.html", task=task, form=form, is_teacher=is_teacher, user=user, responses=responses)
    return render_template("task.html", task=task, form=form, is_teacher=is_teacher, user=user)
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#@app.route('/submit_response/<int:task_id>', methods=['GET','POST'])
#@login_required
#def submit_response(user, task_id):
#    task = Task.query.get(task_id)
#    print(f"==================================================={task.name}=========================================================================")
#    if not task:
#        flash("Zadanie nie istnieje", "error")
#        return redirect(url_for('get_courses'))
#
#    form = forms.TaskResponseForm()
#    print(f"==================================================={task.description}=========================================================================")
#    if form.validate_on_submit():
#        file = form.file.data
#        filename = None
#        if file:
#            original_filename = secure_filename(file.filename)
#            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#            filename = f"{timestamp}_{original_filename}"
#            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#            try:
#                file.save(file_path)
#                flash("File uploaded successfully.", "success")
#            except Exception as e:
#                flash(f"Failed to save file. Error: {e}", "error")
#                return redirect(url_for('task', task_id=task.id))
#        response = TaskResponse(
#            content=form.content.data,
#            task_id=task.id,
#            user_id=user.id,
#            file_path=filename,
#            submitted_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#        )
#        db.session.add(response)
#        db.session.commit()
#        flash("Your response has been submitted.", "success")
#    else:
#        flash("Failed to submit response.", "error")
#    return render_template("submit_response.html", form=form)
#    #return redirect(url_for('task', task_id=task.id))


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
            user.teacher = form.teacher.data    
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


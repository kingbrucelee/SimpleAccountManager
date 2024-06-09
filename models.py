from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), nullable=False,unique=True)
    password = db.Column(db.String(64), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True)
    is_teacher = db.Column(db.Boolean, default=0)
    courses = db.relationship('Course', secondary='enrollment', back_populates='students')
    def __repr__(self):
        return f"<User {self.username}>"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    students = db.relationship('User', secondary='enrollment', back_populates='courses')
    tasks = db.relationship('Task', backref='course', lazy='dynamic')

    def __repr__(self):
        return f"<Course {self.name}>"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    task_type = db.Column(db.Integer)
    start_date = db.Column(db.String(64))
    finish_date = db.Column(db.String(64))
    max_points = db.Column(db.Integer)

    def __repr__(self):
        return f"<Task {self.name}>"

class Enrollment(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    user = db.relationship(User, backref=db.backref("enrollment", cascade="all, delete-orphan"))
    course = db.relationship(Course, backref=db.backref("enrollment", cascade="all, delete-orphan"))

class Permission(db.Model):
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    points = db.Column(db.Integer)

    def __repr__(self):
        return f"<Grade {self.id}>"





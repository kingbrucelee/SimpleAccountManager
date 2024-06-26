from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), nullable=False,unique=True)
    password = db.Column(db.String(64), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True)
    is_teacher = db.Column(db.Boolean, default=False)
    courses = db.relationship('Course', secondary='enrollment', back_populates='students')
    responses = db.relationship('TaskResponse', back_populates='user', lazy='dynamic')
    def __repr__(self):
        return self.login

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

class TaskResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    submitted_at = db.Column(db.String(64))
    file_path = db.Column(db.String(255))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))    
    task = db.relationship('Task', backref='responses')
    user = db.relationship('User', back_populates='responses')
    grade = db.Column(db.Float)

    def __repr__(self):
        return f"<TaskResponse {self.id}>"

    @property
    def is_late(self):
        try:
            submission_time = datetime.strptime(self.submitted_at, "%Y-%m-%d %H:%M:%S")
            due_time = datetime.strptime(self.task.finish_date, "%Y-%m-%d %H:%M:%S")  
            if submission_time > due_time:
                return True
        except Exception as e:
            print(f"DEBUG: Error in is_late calculation: {e}")
        return False


class Enrollment(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    user = db.relationship(User, backref=db.backref("enrollment", cascade="all, delete-orphan"))
    course = db.relationship(Course, backref=db.backref("enrollment", cascade="all, delete-orphan"))
class EnrollmentToAccept(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    user = db.relationship(User, backref=db.backref("pending_enrollment", cascade="all, delete-orphan"))
    course = db.relationship(Course, backref=db.backref("pending_enrollment", cascade="all, delete-orphan"))
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





from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128),nullable=False)
    login = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    # course_admin
    # course_participant
    def __repr__(self):
        return f" Użytkownik {self.login} z hashem hasła {self.password}"
     

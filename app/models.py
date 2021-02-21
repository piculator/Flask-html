from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(20), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    identity = db.Column(db.String(1))
    birthday = db.Column(db.DateTime)
    gender = db.Column(db.String(1))
    about_me = db.Column(db.Unicode(140))
    cloud_storage = db.Column(db.Integer)
    email = db.Column(db.String(120), index=True, unique=True)
    secret_insurance_question = db.Column(db.Unicode(20))
    secret_insurance_answer_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_secret_question(self, question, answer):
        self.secret_insurance_question = question
        self.secret_insurance_answer_hash = generate_password_hash(answer)

    def check_secret_question(self, answer):
        return check_password_hash(self.secret_insurance_answer_hash, answer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#     def __repr__(self):
#         return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

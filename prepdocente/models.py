from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attempts = db.relationship(
        "Attempt",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class InviteCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(120), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    used_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)

    used_by = db.relationship("User", backref="used_invite_code", foreign_keys=[used_by_user_id])


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, unique=True)
    category = db.Column(db.String(120), nullable=False)

    prompt = db.Column(db.Text, nullable=False)

    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)

    correct_option = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(500), nullable=True)


class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    mode = db.Column(db.String(20), default="practice")
    category = db.Column(db.String(120), nullable=True)
    quiz_set = db.Column(db.Integer, default=1)

    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    grade_10 = db.Column(db.Float, default=0.0)
    passed = db.Column(db.Boolean, default=False)

    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship(
        "Answer",
        backref="attempt",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    attempt_id = db.Column(db.Integer, db.ForeignKey("attempt.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    selected_option = db.Column(db.String(1), nullable=True)
    is_correct = db.Column(db.Boolean, default=False)

    question = db.relationship("Question", backref="answers")